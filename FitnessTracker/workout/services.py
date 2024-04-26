def configure_workout(workout, exercises):
    configured_workout = {
        "workout_name": workout.name,
        "pk": workout.pk,
    }

    config = workout.config
    for i in range(len(config)):
        exercise = config[i]
        weights, reps = configure_exercise(exercise["five_rep_max"], exercise["sets"])
        exercise_sets = {"sets": {"weights": weights, "reps": reps}}
        exercises[i].update(exercise_sets)
    configured_workout["exercises"] = exercises
    return configured_workout


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
