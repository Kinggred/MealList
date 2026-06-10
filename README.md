<h1>MealList API</h1>
<h2>Goals</h2>
Goal of this application is to streamline organization in a professional kitchen.
It allows to register ingredients, their cost, caloric data etc. and tie them into specific recipies.
Recipies can be used to plan full meals per x amount of servings and taking into account specific dietary needs of customers via Diets.
Such data makes shopping calculations essentially non-existent as MealList can then sum ingredients necessary to create planned meals and estimate cost among generated shopping list.

<h2>Vocab</h2>
- Ingredient - Specific product or produce 
- Recipe - List of Ingredients with amounts dosed per single serving
- Dish - X amount of servings of specific recipe
- Meal - X amount of Dishes planned to be served at the same time
- Diet - Set of Ingredients allowed to be served.

<h2>Ingredient connectabilty</h2>
To allow for a more streamlined setting of diets it is possible to interconnect Ingredients with each other.
Such many-many relation can define if a certain ingredient contains another one f.e. Butter contains Milk which is important in dietary means 
or alternatively it can be defined as an alternative f.e. Butter - Margarine


<h2>Auth</h2>
Currently standard OAuth2 Password Nearer auth is supported.
All resources are readable for all users, but can be updated by their authors only.

<h2>Database Schema</h2>
![DbSchema.png](docs/DbSchema.png)