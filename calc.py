# weight is measured in kg and height in m
def bmi_calc(weight, height):
    return weight / (height)**2

# Calculates Basal Metabolic Rate, which estrimates how many calories your body uses in a day while completely at rest.
def male_BMR(weight, height, age):
    result = (10*weight) + (6.25*height) - (5*age) + 5
    return result

def female_BMR(weight, height, age):
    result = (10*weight) + (6.25*height) - (5*age) - 161
    return result
# weight is measured in pounds here
def maintenace_cal(BMR, activity_factor):
    return BMR * activity_factor

# made for losing body fat
def cut_cal(maintenace, defperc):
    return maintenace * (1 - defperc)

# made if user wants to gain weight 
def bulk_cal(maintenace, defperc):
    return maintenace * (1 + defperc)