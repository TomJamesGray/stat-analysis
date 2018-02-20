from stat_analysis.d_types.setup import types

def guess_d_type(sample):
    """
    Tries to guess the data type that should be used for the column.
    Can be of any length
    :return: Tuple with a tuple containing d_type name and a reference to a lambda that converts the
    imported string to the chosen data type and a list of strings with possible errors
    caused by this choice
    """
    probs = {
        "int":1.0,
        "float":1.0,
        # "datetime":1.0,
        "string":1.0
    }
    errors = {
        "int":[],
        "float":[],
        "string":[]
    }

    for val in sample:
        points = 0
        numbers = 0
        hyphens = 0
        others = 0
        date_time_chars = 0
        for c in val:
            if c == ".":
                points += 1
            elif c == "-":
                hyphens += 1
            elif c in ["0","1","2","3","4","5","6","7","8","9"]:
                numbers += 1
            elif c in [":","/","_"]:
                date_time_chars += 1
                errors["int"].append(val)
                errors["float"].append(val)
            else:
                others += 1

        if hyphens > 1:
            probs["string"] *= 1.3
            errors["int"].append(val)
            errors["float"].append(val)

        if val == "":
            probs["string"] *= 1.3
            errors["int"].append(val)
            errors["float"].append(val)
            continue

        if points == 1 and numbers == len(val)-1:
            probs["float"] *= 1.5
            probs["string"] *= 0.5

        if others == 0 and date_time_chars == 0 and hyphens <= 1:
            try:
                if int(float(val)) == float(val):
                    probs["int"] *= 1.2
                    probs["float"] *= 0.9
                elif float(val) != int(float(val)):
                    probs["float"] *= 1.2
                    probs["int"] *= 0.6
            except ValueError:
                # Error in parsing value as a number, eg "5432-32"
                probs["float"] *= 0.7
                probs["int"] *= 0.7
                errors["int"].append(val)
                errors["float"].append(val)

        if val[0] == "0" and len(val) == numbers:
            # Probably a phone number?
            probs["string"] *= 1.3

        if len(val) < 20 and date_time_chars >= 1:
            # probs["datetime"] *= 1.5
            # TODO implement datetime format
            probs["string"] *= 1.5

        if others == len(val):
            probs["string"] *= 1.5
            errors["int"].append(val)
            errors["float"].append(val)
        elif others > 0:
            probs["string"] *= 1.05
            errors["int"].append(val)
            errors["float"].append(val)

    # Return maximum value
    chosen_type = max(probs,key=probs.get)
    return (chosen_type, types[chosen_type]["convert"]),errors[chosen_type]