def configure_workout(workout):
    workout_config = {"workout_name": workout.name, "pk": workout.pk, "exercises": []}
    for exercise in workout.config:
        weights, reps = configure_exercise(exercise["five_rep_max"], exercise["sets"])
        workout_config["exercises"].append(
            {exercise["name"]: {"weights": weights, "reps": reps}}
        )
    return workout_config


def configure_exercise(five_rep_max, exercise_sets):
    weights, reps = [], []
    for exercise_set in exercise_sets:
        weight = 0
        match exercise_set["modifier"]:
            case "exact":
                weight = exercise_set["amount"]
            case "percentage":
                weight = (exercise_set["amount"] / 100) * five_rep_max
            case "increment":
                weight = five_rep_max + exercise_set["amount"]
            case "decrement":
                weight = five_rep_max - exercise_set["amount"]
        weights.append(weight)
        reps.append(exercise_set["reps"])
    return weights, reps
