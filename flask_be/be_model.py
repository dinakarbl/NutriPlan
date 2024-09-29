import json
import pandas as pd
from flask import Flask, Response, jsonify, request, send_file
import flask_excel as excel
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)


@app.route('/submit',methods=['POST','GET'])
def submit():
    input_data = request.json
    print(input_data)
    recommendations = recommend_model(input_data)
    print(recommendations)
    return jsonify(recommendations)




def recommend_model(input_data):
    user_input_2= input_data
    all_diets_df = pd.read_csv('All_Diets.csv')
    # Convert height to meters for BMI calculation
    height_m_2 = int(user_input_2['height']) / 100  # Convert from cm to meters
    weight_2 = int(user_input_2['weight'])
    bmi_2 = weight_2 / (height_m_2 ** 2)

    goal_based_calories = {
    "lose weight": {"max_calories": 1800},
    "gain weight": {"min_calories": 2500},
    "maintain weight": {"min_calories": 2000, "max_calories": 2500}
    }
    
    # Filter by dietary goal
    goal_2 = user_input_2['goal'].lower()
    calorie_range_2 = goal_based_calories.get(goal_2, {"min_calories": 1500, "max_calories": 2000})


    # Clean up the dataset: Drop rows with missing values in nutritional fields
    all_diets_df_clean = all_diets_df.dropna(subset=["Protein(g)", "Carbs(g)", "Fat(g)"])

    # Calculate calories based on standard formula: 
    # Total Calories = (Protein * 4) + (Carbs * 4) + (Fat * 9)
    all_diets_df_clean['Calories'] = (
        all_diets_df_clean["Protein(g)"] * 4 +
        all_diets_df_clean["Carbs(g)"] * 4 +
        all_diets_df_clean["Fat(g)"] * 9
    )

    # Filter recipes based on goal and calories
    if "min_calories" in calorie_range_2:
        filtered_df_2 = all_diets_df_clean[all_diets_df_clean['Calories'] >= calorie_range_2['min_calories']]
    else:
        filtered_df_2 = all_diets_df_clean

    if "max_calories" in calorie_range_2:
        filtered_df_2 = filtered_df_2[filtered_df_2['Calories'] <= calorie_range_2['max_calories']]

    # Exclude dishes with allergens mentioned in the user's input
    if user_input_2["allergies"]:
        allergies_2 = user_input_2["allergies"]
        filtered_df_2 = filtered_df_2[~filtered_df_2['Recipe_name'].str.contains('|'.join(allergies_2), case=False, na=False)]

    # Select top 10 recommendations based on calorie count closest to user's goal
    recommended_dishes_2 = filtered_df_2.head(3)
    

    # Output the recommended dishes in JSON format
    top_recommendations = recommended_dishes_json_2 = recommended_dishes_2[["Diet_type", "Recipe_name", "Cuisine_type", "Calories"]].to_dict(orient="records")

    return top_recommendations

if __name__ == '__main__':
    excel.init_excel(app)
    app.run(debug=True)