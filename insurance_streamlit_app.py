import streamlit as st
import ollama
import requests
from datetime import datetime
import base64

## To run this application, run `pip install -r requirements.txt` first to install the required packages, then run `streamlit run ./insurance_streamlit_app.py` from the terminal - be sure to change your directory to where the file is located before running

# Initialize Streamlit app
st.title("Home Damage Assessment")
st.write("Upload images of the damages sustained to your home, include the date of occurence and provide a description of the images and the incident to receive a full damage report.")

# Inputs from the user

images = st.file_uploader("Upload images of home damage (PNG, JPG, and JPEG files only)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
incident_date = st.date_input("Date of Occurence")
zip_code = st.text_input("Zip Code of the Incident")
user_description = st.text_area("Short Description of the Incident")

# Button to process inputs
if st.button("Analyze"):
    if not images or not zip_code or not user_description:
        st.error("Please fill in all inputs and upload at least oneß image.")
    else:
        st.write("Processing report...")

        # Connect to Ollama for LLM processing
        
        photo_summaries = []

        # Convert images to base64
        images_b64 = []
        for image in images:
            image_b64 = base64.b64encode(image.read()).decode('utf-8')
            images_b64.append(image_b64)

        
        # Send image to LLM for analysis
        ## TO DO: Need to have vision model and granite model downloaded in Ollama to run out of the box
        ## 1. Download Ollama at https://ollama.com 
        ## 2. Run `ollama pull llama3.2-vision:11b` in Terminal
        ## 3. Run `ollama pull granite3-dense:8b` in Terminal (or whatever model you'd like to do the LLM summary of the images)
        ## Ready to go!
        response = ollama.chat(model='llama3.2-vision',
                    messages=[
                        {"role": "user", "content": "The photo shared with you is an image shared by an Homeowner's insurance policyholder trying to make a claim for damage to their home. Pleas write a description for what is in the image and make a best guess at what likely happened to cause the damage. Determine whether or not a contractor wouold likely be required to fix the damage.", "images": images_b64}
                    ]
                )
        photo_summary = response["message"]["content"]
        photo_summaries.append(photo_summary)

        # Display photo summaries
        st.subheader("Photo Summaries")
        for i, summary in enumerate(photo_summaries):
            st.image(images[i], caption=f"Image {i+1}")
            st.write(f"Summary: {summary}")

        # Compare user description with photo summaries
        st.subheader("Comparison of User Description of Image and AI Image Interpretation")
        for i, photo_summary in enumerate(photo_summaries):
            st.write(f"Image {i+1} Comparison:")
            # Feel free to change the model, just be sure to pull it via Ollama beforehand
            compare_response = ollama.chat(model='granite3-dense:8b',
                    messages=[
                        {"role": "user", "content": f"""
                         Two descriptions of an image have been provided regarding a home damage insurance claim. Compare the policyholder's description of the images and accident with the AI generated description of the picture and decide whether they are talking about the same incident.
                         Respond only with "Follow up investigation suggested to verify validity" if the two summarires are not talking about the same incident. Otherwise, respond with "User description matches. No discrepancies noted."
                         Policyholder description of incident: {user_description}
                         AI generated description of Image: {photo_summary}
                         """}
                    ]
                )
            st.write(compare_response["message"]["content"])

        # Fetch weather data
        ## TO DO: Create Account with WeatherAPI at https://www.weatherapi.com/signup.aspx
        ## Retrieve your API key and replace below
        ## NOTE: If you just created the account you will have access to a pro plan which allows you to pull historical weather. 
        # If your free trial has ended and you are now on the free tier plan, you will not be able to pull historical weather and may get an error. 
        # Keep this in mind when testing and entering in a date that is prior to today in the UI.
        weather_api_key = "PASTE_YOUR_API_KEY_HERE"  # Replace with your actual API key
        weather_url = f"http://api.weatherapi.com/v1/history.json?key={weather_api_key}&q={zip_code}&dt={incident_date}"

        try:
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()
            location_city = weather_data['location']['name']
            location_state = weather_data['location']['region']
            weather_conditions = weather_data.get("forecast", {}).get("forecastday", [])[0].get("day", {})

            st.subheader(f"Weather on the Date of Incident in {location_city}, {location_state}")
            if weather_conditions:
                condition_text = weather_conditions.get("condition", {}).get("text", "Unknown")
                wind_max = weather_conditions.get("maxwind_mph",'N/A')
                precipitation = weather_conditions.get("totalprecip_in",'N/A')
                max_temp = weather_conditions.get("maxtemp_f", "N/A")
                min_temp = weather_conditions.get("mintemp_f", "N/A")
                humidity = weather_conditions.get("avghumidity",'N/A')
                weather_response = ollama.chat(model='granite3-dense:8b',
                    messages=[
                        {"role": "user", "content": f"""The following weather report is being used for an homeowners insurance claim. Based on the AI generated description of an image shared by the policyholder for the claim and the weather report for the day, determine whether the current conditions for the day may have impacted the incident.
                            Policyholder Image Description for Insurance claim: {photo_summary}   
                        
                            Weather Report for {location_city}, {location_state} on {incident_date}. 
                            Condition: {condition_text}
                            Max Wind: {wind_max} mph
                            Total Precipitation: {precipitation} inches
                            Max Temp: {max_temp}°F
                            Min Temp: {min_temp}°F
                            Averge Humidity: {humidity}%
                        """ }
                    ]
                )

                st.write(f"Condition: {condition_text}")
                st.write(f"Max Wind: {wind_max} mph")
                st.write(f"Total Precipitation: {precipitation} inches")
                st.write(f"Max Temp: {max_temp}°F")
                st.write(f"Min Temp: {min_temp}°F")
                st.write(f"Averge Humidity: {humidity}%")
                st.write(weather_response['message']['content'])
                st.write()
            else:
                st.write("Weather data not available.")
        except Exception as e:
            st.error("Error fetching weather data: " + str(e))



        
        
        
        
        



        


