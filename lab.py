"""
6.1010 Spring '23 Lab 4: Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def make_recipe_book(recipes, forbidden_items=None):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    dictionary = {}
    for food_info in recipes:
        if food_info[0] == "compound":
            if forbidden_items and food_info[1] in forbidden_items:
                continue
            if food_info[1] in dictionary:
                dictionary[food_info[1]].append(food_info[2])
            else:
                dictionary[food_info[1]] = [food_info[2]]
    return dictionary


def make_atomic_costs(recipes, forbidden_items=None):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    dictionary = {}
    for food_info in recipes:
        if food_info[0] == "atomic":
            if forbidden_items and food_info[1] in forbidden_items:
                continue
            dictionary[food_info[1]] = food_info[2]
    return dictionary


def lowest_cost(recipes, food_item, forbidden_items=None):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    atomic_food_dict = make_atomic_costs(recipes, forbidden_items)
    compound_food_dict = make_recipe_book(recipes, forbidden_items)
    if food_item not in atomic_food_dict and food_item not in compound_food_dict:
        return None

    if food_item in atomic_food_dict:
        return atomic_food_dict[food_item]

    diff_variations = compound_food_dict[food_item]
    diff_variations_costs = []
    for this_variation in diff_variations:
        is_makable = True
        this_variation_cost = 0
        for ingredient in this_variation:
            lowest_cost_for_ingredient = lowest_cost(
                recipes, ingredient[0], forbidden_items
            )
            if lowest_cost_for_ingredient == None:
                is_makable = False
                break
            this_variation_cost += ingredient[1] * lowest_cost_for_ingredient
        if is_makable:
            diff_variations_costs.append(this_variation_cost)
    if diff_variations_costs:
        return min(diff_variations_costs)
    return None


def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    scaled_flat_recipe = flat_recipe.copy()
    for ingredient in scaled_flat_recipe:
        scaled_flat_recipe[ingredient] *= n
    return scaled_flat_recipe


def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    grocery_list = {}
    for flat_recipe in flat_recipes:
        for ingredient in flat_recipe:
            if ingredient in grocery_list:
                grocery_list[ingredient] += flat_recipe[ingredient]
            else:
                grocery_list[ingredient] = flat_recipe[ingredient]
    return grocery_list


def cheapest_flat_recipe(recipes, food_item, forbidden_items=None):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    atomic_food_dict = make_atomic_costs(recipes, forbidden_items)
    compound_food_dict = make_recipe_book(recipes, forbidden_items)
    dictionary = {}
    if food_item not in atomic_food_dict and food_item not in compound_food_dict:
        return None

    if food_item in atomic_food_dict:
        dictionary[food_item] = 1
        return dictionary

    diff_variations = compound_food_dict[food_item]
    diff_variations_costs = []
    diff_variations_dicts = []
    for this_variation in diff_variations:
        is_makable = True
        this_variation_cost = 0
        this_variation_dict = []
        for ingredient in this_variation:
            lowest_cost_for_ingredient = lowest_cost(
                recipes, ingredient[0], forbidden_items
            )
            if lowest_cost_for_ingredient == None:
                is_makable = False
                break
            this_variation_cost += ingredient[1] * lowest_cost_for_ingredient
            this_variation_dict.append(
                scale_recipe(
                    cheapest_flat_recipe(recipes, ingredient[0], forbidden_items),
                    ingredient[1],
                )
            )
        if is_makable:
            diff_variations_costs.append(this_variation_cost)
            diff_variations_dicts.append(make_grocery_list(this_variation_dict))
    if diff_variations_costs:
        least_cost = min(diff_variations_costs)
        min_index = diff_variations_costs.index(least_cost)
        return diff_variations_dicts[min_index]
    return None


def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes make a certain ingredient as part of a recipe, compute all
    combinations of the flat recipes.
    """
    if len(flat_recipes) == 1:
        return [ingredient for ingredient in flat_recipes[0]]
    all_mixes = []
    for ingredient in flat_recipes[0]:
        for other_mixes in ingredient_mixes(flat_recipes[1:]):
            grocery_list = make_grocery_list([ingredient, other_mixes])
            all_mixes.append(grocery_list)
    return all_mixes


def all_flat_recipes(recipes, food_item, forbidden_items=[]):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic_food_dict = make_atomic_costs(recipes, forbidden_items)
    compound_food_dict = make_recipe_book(recipes, forbidden_items)
    if food_item not in atomic_food_dict and food_item not in compound_food_dict:
        return []

    if food_item in atomic_food_dict:
        return [{food_item: 1}]

    result = []
    for this_variation in compound_food_dict[food_item]:
        mix_input = []
        is_makeable = True
        for ingredient in this_variation:
            var_of_ingredient = []
            if not ingredients_present(recipes, ingredient[0], forbidden_items):
                is_makeable = False
                break
            for ingredient_recipe in all_flat_recipes(
                recipes, ingredient[0], forbidden_items
            ):
                var_of_ingredient.append(scale_recipe(ingredient_recipe, ingredient[1]))
            mix_input.append(var_of_ingredient)
        if is_makeable:
            result.extend(ingredient_mixes(mix_input))
    return result


def ingredients_present(recipes, food_item, forbidden_items=[]):
    if lowest_cost(recipes, food_item, forbidden_items) == None:
        return False
    return True


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
