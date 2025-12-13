import streamlit as st
import requests

LIST_INGREDIENTS_URL = 'https://www.themealdb.com/api/json/v1/1/list.php?i=list?'
LIST_MEALS_BY_FIRST_LETTER_URL = 'https://www.themealdb.com/api/json/v1/1/search.php?f=a'
LIST_SEARCH_MEALS_BY_NAME_URL = 'https://www.themealdb.com/api/json/v1/1/search.php?s='

if "count" not in st.session_state:
    st.session_state["count"] = 0
    
def increment_counter():
    st.session_state["count"] += 1

def get_list_of_ingredients(input):
    try:
        # Make the API request
        response = requests.get(
            f"{LIST_INGREDIENTS_URL}"
        )

        # Check if the request was successful
        if response.status_code == 200:
            json_format = response.json()
            ingredients = []

            print(json_format) 

            for item in json_format:
                # Ensure necessary keys exist
                if "input" in item["strMeal"] and "strIngredient" in item:
                    ingredients.append(item["input"]["strIngrediants"])
                else:
                    print("Item is missing required fields.")

            if ingredients:
                return ingredients
            else:
                print("No products found.")
                return []

        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        # Handle any exceptions during the request
        print(f"An error occurred: {e}")
        return []
    
def get_list_of_meals_by_first_letter():
    try:
        # Make the API request
        response = requests.get(
            f"{LIST_MEALS_BY_FIRST_LETTER_URL}"
        )

        # Check if the request was successful
        if response.status_code == 200:
            json_format = response.json()
            meals = []
            meals_pictures = []
            list_needs = []

            #print(json_format)

            for item in json_format["meals"]:
                # Ensure necessary keys exist
                if "strMeal" in item:
                    meals.append(item["strMeal"])
                    #print("wwwwwwwwwwwwwwwwwwwwwwwwwwwww", item['meals'])
                else:
                    print("Item is missing required fields.")

                if "strMealThumb" in item:
                    meals_pictures.append(item["strMealThumb"])
                    #print("nnnnnnnnnnnnnnnnnn", meals_pictures)

            
            if meals and meals_pictures:
                 list_needs.append(meals)
                 list_needs.append(meals_pictures)
                 return[list_needs]
                 
            else:
                print("No products found.")
                
                return []

        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []


    except Exception as e:
        # Handle any exceptions during the request
        print(f"An error occurred: {e}")
        return []



def get_list_of_ingredients(input):
    try:
        # Make the API request
        response = requests.get(
            f"{LIST_INGREDIENTS_URL}"
        )

        # Check if the request was successful
        if response.status_code == 200:
            json_format = response.json()
            ingredients = []

            print(json_format)

            for item in json_format:
                # Ensure necessary keys exist
                if "strIngredient" in item:
                    ingredients.append(item["strIngredient"])
                else:
                    print("Item is missing required fields.")

            if ingredients:
                return ingredients
            else:
                print("No products found.")
                return []

        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        # Handle any exceptions during the request
        print(f"An error occurred: {e}")
        return []


def main():

    # Call the function and handle the results
    meals = get_list_of_meals_by_first_letter()

    def search_meals(query):
        # Filter meals based on the query
        return [meal for meal in meals if query.lower() in meal["name"].lower()]
    print(meals[0])

    # Combine meals with their corresponding images
   


    selected_value = st.selectbox(
        "Search meal ingredients.... ", 
         meals[0][0],
    )
    
        

    Ingrediants = get_list_of_ingredients(selected_value)
    st.title("Supermarket")
    # pass search function and other options as needed

    #inputs = st.selectbox("Select ingredient:", listers)
    # if listers:
    #     print(f"Available products: {listers}")
    # else:
    #     print("No products available.")

if __name__ == "__main__":
    main()
