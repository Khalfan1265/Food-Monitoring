import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class FoodRecommender:
    def __init__(self, dbname='food_monitoring', user='postgres', password='root', host='localhost', port='5432'):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()
        
    def __del__(self):
        self.cur.close()
        self.conn.close()
    
    def get_user_health_data(self, user_id: str) -> Optional[Dict]:
        """Get the latest health data for a user"""
        query = """
        SELECT heart_rate_bpm, systolic_bp, diastolic_bp, measurement_time 
        FROM health 
        WHERE user_id = %s 
        ORDER BY measurement_time DESC 
        LIMIT 1
        """
        self.cur.execute(query, (user_id,))
        result = self.cur.fetchone()
        
        if not result:
            return None
            
        return {
            'heart_rate': result[0],
            'systolic_bp': result[1],
            'diastolic_bp': result[2],
            'measurement_time': result[3]
        }
    
    def get_user_allergies(self, user_id: str) -> List[str]:
        """Get all allergies for a user"""
        query = "SELECT allergy_type FROM allergy WHERE user_id = %s"
        self.cur.execute(query, (user_id,))
        return [row[0] for row in self.cur.fetchall()]
    
    def get_recent_food_intake(self, user_id: str, hours: int = 24) -> List[Dict]:
        """Get food consumed by user in last X hours"""
        query = """
        SELECT meal_type, food_items, calories_estimate, intake_time 
        FROM food 
        WHERE user_id = %s AND intake_time >= %s
        ORDER BY intake_time DESC
        """
        time_threshold = datetime.now() - timedelta(hours=hours)
        self.cur.execute(query, (user_id, time_threshold))
        
        return [
            {
                'meal_type': row[0],
                'food_items': row[1],
                'calories': row[2],
                'time': row[3]
            }
            for row in self.cur.fetchall()
        ]
    
    def get_recent_drinks(self, user_id: str, hours: int = 24) -> List[Dict]:
        """Get drinks consumed by user in last X hours"""
        query = """
        SELECT drink_type, volume_ml, sugar_g, drink_time 
        FROM drink 
        WHERE user_id = %s AND drink_time >= %s
        ORDER BY drink_time DESC
        """
        time_threshold = datetime.now() - timedelta(hours=hours)
        self.cur.execute(query, (user_id, time_threshold))
        
        return [
            {
                'drink_type': row[0],
                'volume_ml': row[1],
                'sugar_g': row[2],
                'time': row[3]
            }
            for row in self.cur.fetchall()
        ]
    
    def analyze_blood_pressure(self, systolic: int, diastolic: int) -> str:
        """Categorize blood pressure level"""
        if systolic < 90 or diastolic < 60:
            return "Low BP"
        elif systolic >= 140 or diastolic >= 90:
            return "High BP"
        else:
            return "Normal"
    
    def generate_recommendations(self, user_id: str) -> Dict:
        """Generate personalized food recommendations"""
        # Get user data
        health_data = self.get_user_health_data(user_id)
        if not health_data:
            return {"error": "No health data available for this user"}
            
        allergies = self.get_user_allergies(user_id)
        recent_food = self.get_recent_food_intake(user_id)
        recent_drinks = self.get_recent_drinks(user_id)
        
        # Analyze health metrics
        bp_status = self.analyze_blood_pressure(
            health_data['systolic_bp'], 
            health_data['diastolic_bp']
        )
        
        # Calculate total recent calories
        total_calories = sum(f['calories'] for f in recent_food if f['calories'])
        
        # Analyze hydration
        water_intake = sum(
            d['volume_ml'] for d in recent_drinks 
            if d['drink_type'] == 'Water'
        )
        sugar_intake = sum(
            d['sugar_g'] for d in recent_drinks 
            if d['sugar_g'] is not None
        )
        
        # Generate recommendations based on analysis
        recommendations = {
            'general_advice': [],
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': [],
            'hydration': []
        }
        
        # Blood pressure specific recommendations
        if bp_status == "High BP":
            recommendations['general_advice'].append(
                "Your blood pressure is high. Consider foods rich in potassium, magnesium, and fiber."
            )
            recommendations['general_advice'].append(
                "Reduce sodium intake and avoid processed foods."
            )
            safe_foods = [
                "Oatmeal with berries",
                "Leafy green vegetables",
                "Bananas",
                "Fatty fish (salmon, mackerel)",
                "Beets",
                "Garlic",
                "Dark chocolate (in moderation)"
            ]
        elif bp_status == "Low BP":
            recommendations['general_advice'].append(
                "Your blood pressure is low. Consider slightly increasing sodium intake and staying hydrated."
            )
            safe_foods = [
                "Small, frequent meals",
                "Salty snacks like nuts or pretzels",
                "Caffeinated beverages in moderation",
                "Foods rich in vitamin B12 (eggs, meat, dairy)",
                "Licorice tea (can help raise BP)"
            ]
        else:  # Normal BP
            recommendations['general_advice'].append(
                "Your blood pressure is normal. Maintain a balanced diet."
            )
            safe_foods = [
                "Whole grains",
                "Lean proteins",
                "Variety of fruits and vegetables",
                "Healthy fats (avocados, nuts, olive oil)"
            ]
        
        # Filter foods based on allergies
        if "Peanut Allergy" in allergies:
            safe_foods = [f for f in safe_foods if "peanut" not in f.lower()]
            recommendations['general_advice'].append(
                "Avoiding peanuts and peanut products due to allergy."
            )
        if "Lactose Intolerance" in allergies:
            safe_foods = [f for f in safe_foods if "dairy" not in f.lower() and "cheese" not in f.lower()]
            recommendations['general_advice'].append(
                "Choosing lactose-free alternatives due to lactose intolerance."
            )
        
        # Hydration recommendations
        if water_intake < 2000:  # less than 2L
            recommendations['hydration'].append(
                f"Your recent water intake is {water_intake}ml. Aim for at least 2L per day."
            )
        if sugar_intake > 50:  # more than 50g
            recommendations['hydration'].append(
                f"Your recent sugar intake from drinks is {sugar_intake}g. Consider reducing sugary beverages."
            )
        
        # Meal suggestions
        recommendations['breakfast'] = [
            f for f in safe_foods 
            if "mihogo" in f.lower() or 
               "supu with chapati" in f.lower() or 
               "eggs" in f.lower() or
               "tea" in f.lower() or
               "coffee" in f.lower() or
               "maandazi" in f.lower() or
               "mtori" in f.lower()
        ][:7]  # Limit to 7 suggestions
        
        recommendations['lunch'] = [
            f for f in safe_foods 
            if "wali nyama" in f.lower() or 
               "wali njegere" in f.lower() or 
               "pilau kuku" in f.lower() or
               "ugali nyama" in f.lower() or
               "ugali samaki" in f.lower() or
               "ugali mboga" in f.lower() or
               "ugali kuku" in f.lower() or
               "wali samaki" in f.lower() or
               "wali mboga" in f.lower() or
               "wali bamia" in f.lower() or
               "wali maharage" in f.lower()
        ][:11]  # Limit to 11 suggestions
        
        recommendations['dinner'] = [
            f for f in safe_foods 
            if "wali njegere" in f.lower() or 
               "wali samaki" in f.lower() or
               "wali mboga" in f.lower() or
               "wali bamia" in f.lower() or
               "wali maharage" in f.lower() or
               "wali nyama" in f.lower()
        ][:6]
        
        recommendations['snacks'] = [
            f for f in safe_foods 
            if "nuts" in f.lower() or 
               "dark chocolate" in f.lower() or 
               "fruit" in f.lower() or
               "yogurt" in f.lower() or
               "drink" in f.lower()
        ][:3]
        
        return recommendations
    
    def print_recommendations(self, user_id: str):
        """Print formatted recommendations for a user"""
        recommendations = self.generate_recommendations(user_id)
        
        if 'error' in recommendations:
            print(recommendations['error'])
            return
            
        print("\n=== Personalized Food Recommendations ===")
        print(f"\nUser ID: {user_id}")
        
        # Print general advice
        print("\nGeneral Dietary Advice:")
        for advice in recommendations['general_advice']:
            print(f"- {advice}")
        
        # Print meal suggestions
        print("\nMeal Suggestions:")
        print("\nBreakfast:")
        for item in recommendations['breakfast']:
            print(f"- {item}")
            
        print("\nLunch:")
        for item in recommendations['lunch']:
            print(f"- {item}")
            
        print("\nDinner:")
        for item in recommendations['dinner']:
            print(f"- {item}")
            
        print("\nSnacks:")
        for item in recommendations['snacks']:
            print(f"- {item}")
        
        # Print hydration advice
        if recommendations['hydration']:
            print("\nHydration Advice:")
            for advice in recommendations['hydration']:
                print(f"- {advice}")


# Example usage
if __name__ == "__main__":
    # Initialize the recommender
    recommender = FoodRecommender(
        dbname='food_monitoring',
        user='postgres',
        password='root',  # Replace with your actual password
        host='localhost',
        port='5432'
    )
    
    # Get a sample user ID from the database
    recommender.cur.execute("SELECT user_id FROM student LIMIT 1")
    user_id = recommender.cur.fetchone()[0]
    
    # Generate and print recommendations
    recommender.print_recommendations(user_id)