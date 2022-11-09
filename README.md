# Police-Brutality

Intro :
Our objective is to assess this dataset and identify further findings to help those protesting needless killing as well as provide a foundation for the ongoing movement.
This way we could also suggest areas where the police department could make improvements

Dataset link : https://www.kaggle.com/datasets/ahsen1330/us-police-shootings

Dataset Description :
Made use of 4 datasets : 
1) Police shootings dataset :

id: a unique identifier for each victim
name: the name of the victim
date: the date of the fatal shooting in YYYY-MM-DD format
manner_of_death: shot, shot and Tasered
armed: indicates that the victim was armed with some sort of implement that a police officer believed could inflict harm
undetermined: it is not known whether or not the victim had a weapon
unknown: the victim was armed, but it is not known what the object was
unarmed: the victim was not armed
age: the age of the victim
gender: the gender of the victim. The Post identifies victims by the gender they identify with if reports indicate that it differs from their biological sex.

race:
W: White, non-Hispanic
B: Black, non-Hispanic
A: Asian
N: Native American
H: Hispanic
O: Other
None: unknown

city: the municipality where the fatal shooting took place. Note that in some cases this field may contain a county name if a more specific municipality is unavailable or unknown.

state: two-letter postal code abbreviation
signs of mental illness: News reports have indicated the victim had a history of mental health issues, expressed suicidal intentions or was experiencing mental distress at the time of the shooting.

threat_level: The threat_level column was used to flag incidents for the story by Amy Brittain in October 2015. http://www.washingtonpost.com/sf/investigative/2015/10/24/on-duty-under-fire/ As described in the story, the general criteria for the attack label was that there was the most direct and immediate threat to life. That would include incidents where officers or others were shot at, threatened with a gun, attacked with other weapons or physical force, etc. The attack category is meant to flag the highest level of threat. The other and undetermined categories represent all remaining cases. Other includes many incidents where officers or others faced significant threats.

flee: News reports have indicated the victim was moving away from officers
Foot
Car
Not fleeing
The threat column and the fleeing column are not necessarily related. For example, there is an incident in which the suspect is fleeing and at the same time turns to fire at gun at the officer. Also, attacks represent a status immediately before fatal shots by police while fleeing could begin slightly earlier and involve a chase.

body_camera: News reports have indicated an officer was wearing a body camera and it may have recorded some portion of the incident.

2) Median Household income 2015 :

Geographic Area : two-letter postal code abbreviation of the state that the cities belong to

City :  the municipality where the fatal shooting took place. Note that in some cases this field may contain a county name if a more specific municipality is unavailable or unknown.

Median Income :The median household income in 2015 for the corresponding city 

3) PercentagePeopleBelowPovertyLevel :

Geographic Area : two-letter postal code abbreviation of the state that the cities belong to

City :  the municipality where the fatal shooting took place. Note that in some cases this field may contain a county name if a more specific municipality is unavailable or unknown.

poverty_rate : The corresponding poverty rate in the city 

4) ShareRaceByCity : 

Geographic Area : two-letter postal code abbreviation of the state that the cities belong to

City :  the municipality where the fatal shooting took place. Note that in some cases this field may contain a county name if a more specific municipality is unavailable or unknown.

share_white : % of white raced people in the area
share_black : % of black raced people in the area
share_hispanic : % of hispanic people in the area 
share_asian : % of asian people in the area 
share_native : % of native american raced people in the area 

Inferences : 

Police Killings :
white raced people are killed most followed by black and hispanic raced people in second and third respectively

Victims of police shootings are found to be highest from ages 18 to 51

95.8% of the victims are Male with only 4.19% female victims

majority of victims were armed with a gun

74.9% of victims showed no signs of a mental illness

An astounding number of victims did not try to flee or escape

Majority of the victims were classified with a threat level "attack"

States with most killings : CA(383) TX(211) FL(142)

Median Income :

Highest CA(156K)

Poverty Rates :

Highest AL(78.8),FL(33.6). Some of the Lowest CA(2.5),TX(9.7)

Race By City :

Highest Native American Percentage is in Arkansas
Highest Black percentage is in Washington DC
Highest Asian percentage is in Hawaii
Highest Hispanic percentage is in Texas
Highest White percentage is in Vermont

