def calculate_calories_and_macros(weight, height, age, gender, activity_level, goal):
    """
    Berechnet den täglichen Kalorienbedarf (TDEE) und die Makronährstoffe.
    """
    # 1. Grundumsatz berechnen (BMR - Basal Metabolic Rate) nach Mifflin-St. Jeor
    # Hinweis: Da wir Alter und Geschlecht noch nicht im Profil abfragen, 
    # nutzen wir für den Prototyp erstmal Durchschnittswerte (Alter 30, Männlich),
    # falls sie nicht übergeben werden.
    if gender == "Männlich":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # 2. Aktivitäts-Multiplikator anwenden (TDEE)
    multipliers = {
        "Niedrig (1-2x pro Woche)": 1.2,
        "Mittel (3-4x pro Woche)": 1.55,
        "Hoch (5-6x pro Woche)": 1.725,
        "Extrem (Täglich)": 1.9
    }
    # Falls der Wert aus der DB nicht im Dictionary ist, nehmen wir "Mittel" als Fallback
    multiplier = multipliers.get(activity_level, 1.55) 
    tdee = bmr * multiplier

    # 3. Ziel-Anpassung (Defizit oder Überschuss)
    if goal == "Abnehmen":
        target_calories = tdee - 500  # 500 kcal Defizit
    elif goal == "Muskelaufbau":
        target_calories = tdee + 300  # 300 kcal Überschuss
    else:
        target_calories = tdee  # Gewicht halten / Ausdauer

    target_calories = int(target_calories)

    # 4. Makros berechnen (Grobe Daumenregel für Fitness)
    # Protein: ca. 2g pro kg Körpergewicht
    protein = int(weight * 2.0)
    
    # Fett: ca. 1g pro kg Körpergewicht (oder ca. 25% der Kalorien)
    fett = int(weight * 1.0)
    
    # Kohlenhydrate: Der restliche Kalorienbedarf
    # 1g Protein = 4 kcal, 1g Fett = 9 kcal, 1g Carbs = 4 kcal
    rest_kalorien = target_calories - (protein * 4) - (fett * 9)
    carbs = int(rest_kalorien / 4)

    return {
        "kalorien": target_calories,
        "protein": protein,
        "fett": fett,
        "carbs": carbs
    }

# Die eigentlichen Funktionen
def calculate_bmi(weight, height_cm):
    """Berechnet den Body Mass Index (BMI)."""
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 1)

def calculate_target_calories(weight, height_cm, age, gender, activity_level, goal):
    """
    Berechnet den Kalorienbedarf basierend auf Harris-Benedict.
    Gibt die Kalorien als ganze Zahl zurück.
    """
    # Grundumsatz (BMR) berechnen
    if gender == "Männlich":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height_cm) - (5.677 * age)
    else:
        # Weiblich
        bmr = 447.593 + (9.247 * weight) + (3.098 * height_cm) - (4.330 * age)

    # Aktivitätsfaktor (PAL)
    activity_multipliers = {
        "Wenig (Bürojob, kein Sport)": 1.2,
        "Leicht (1-2x Sport/Woche)": 1.375,
        "Mittel (3-5x Sport/Woche)": 1.55,
        "Hoch (6-7x Sport/Woche)": 1.725
    }
    
    # Standardwert ist 1.2 falls was schiefgeht
    pal = activity_multipliers.get(activity_level, 1.2)
    tdee = bmr * pal

    # Ziel-Anpassung
    if goal == "Abnehmen":
        target = tdee - 500  # 500 kcal Defizit
    elif goal == "Muskelaufbau":
        target = tdee + 300  # 300 kcal Überschuss
    else:
        target = tdee  # Gewicht halten

    return int(round(target))