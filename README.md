## Project Overview : Rule Engine with AST

This project implements a rule engine capable of evaluating complex rules expressed as Abstract Syntax Trees (ASTs). It utilizes a Django backend for data storage and processing.

**Data Model**

The core data model is defined by the `rules` class:

| Field Name | Description |
|---|---|
| rule_name |  A human-readable name for the rule (CharField). |
| rule_string | The original rule expression as a string (TextField). |
| rule_ast | The serialized JSON representation of the rule's AST (JSONField). |

**Rule Processing**

1. **Rule Creation:**
   - Users define rules using a string expression (e.g., "age > 30 AND income > 50000").
   - The `create_rule` function validates the rule string format:
      - Ensures balanced parentheses.
      - Removes redundant parentheses.
      - Checks for valid comparison operators (>, <, >=, <=, =).
   - The function parses the validated string and constructs the corresponding AST.
   - The AST is serialized to JSON and stored in the `rule_ast` field.

2. **Rule Evaluation:**
   - The `evaluate_ast` function takes an AST and a data dictionary as input.
   - It recursively traverses the AST, evaluating conditions based on the data values.
   - Supported operators include AND (`&`) and OR (`|`).

**API Endpoints:**

- `/rules/`: Provides CRUD operations for managing rules using the `ruleStoreViewSet` class.
    - POST: Creates a new rule by validating the rule string, constructing the AST, and storing it in the database.
    - GET (list): Retrieves a list of all rules.
    - GET (detail): Retrieves a specific rule by ID.
    - PUT: Updates an existing rule.
    - DELETE: Deletes a rule.
- `/rules/<id>/evaluate/`: Evaluates a specific rule (by ID) against provided data using the `ruleEvaluate` class.
    - POST: Takes data as input and returns the evaluated result (True/False) based on the rule's AST.
- `/rules/combine/`: Combines multiple existing rules into a new rule using the `CombineRules` class.
    - POST: Takes an array of rule IDs and a desired name for the combined rule.
    - Creates a new rule by:
        - Finding the most frequent operator (AND or OR) used in the individual rules.
        - Combining the ASTs of the selected rules using the frequent operator.
        - Serializing the combined AST and storing the new rule in the database.

**Inner Workings:**

* **Rule Creation:**
    - The `create_rule` function uses a recursive descent parser to break down the rule string into tokens (operands and operators).
    - It constructs an AST by creating nodes for each operand and operator, linking them together based on the rule's structure.
    - The AST represents the logical flow of the rule, where operands are compared and combined using operators.
* **Rule Evaluation:**
    - The `evaluate_ast` function recursively traverses the AST:
        - For operand nodes (conditions), it evaluates the condition using the provided data.
        - For operator nodes (AND, OR), it evaluates the left and right subtrees and combines the results based on the operator's logic.
* **Rule Combining:**
    - The `CombineRules` class combines multiple existing rules into a single rule.
    - It first analyzes the ASTs of the individual rules to determine the most frequently used operator (AND or OR).
    - Then, it iteratively merges the rules, starting with the first rule and combining it with the subsequent rules using the chosen operator.
    - The resulting combined AST represents the logical conjunction or disjunction of the original rules.

**Explanation of Key Concepts:**

- **AST (Abstract Syntax Tree):** A tree-like data structure that represents the syntactic structure of a rule expression. Each node in the AST corresponds to an operand or operator in the rule.
- **Operand:** A basic unit of a rule, typically a comparison between a field and a value (e.g., "age > 30").
- **Operator:** Connects operands to form more complex expressions (e.g., "AND", "OR").
- **Recursive Descent Parsing:** A top-down parsing technique used to analyze the rule string and construct the AST.
- **Data Dictionary:** A dictionary containing key-value pairs representing the data against which the rule is evaluated.

**Important: Data Entry for Rule Evaluation**

When submitting data for rule evaluation, users should adhere to the following guidelines:

- **JSON Format:** The data must be structured in valid JSON format. Ensure that the input data adheres to the expected structure defined by the rules you want to evaluate.
- **Required Fields:** The input data must include all fields referenced in the rule's conditions. For example, if the rule checks age and department, the input must provide values for both:

```json
{
    "age": 35,
    "department": "HR"
}
```

**Additional Notes:**

- The project uses the Django REST framework for building APIs to interact with the rule engine.
- The `RuleCombiner` class provides a flexible mechanism for combining rules based on their logical structure.
- The rule engine can be extended to support more complex operators or data types as needed.


## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**

Clone the GitHub repository to your local machine using the following command:

```bash
git clone https://github.com/your_username/your_repo_name.git
```

2. **Navigate to the Project Directory**

Navigate to the project directory after cloning:

```bash
cd your_repo_name
```

3. **Install Dependencies**

Use Pipenv to install the required dependencies specified in the Pipfile:
if pipenv is not present , use the command

``` bash
pip install pipenv
```
if present , then 

```bash
pipenv install
```

4. **Generate a Secret Key**

Generate a secure `SECRET_KEY` for your Django project by running this Python script:

```python
import secrets
print(secrets.token_urlsafe(50))
```

Copy the generated key.

5. **Set the Secret Key**

There are two ways to set your secret key:

**Option 1: Edit settings.py**

Replace the `SECRET_KEY` in `settings.py` with your newly generated key:

```python
SECRET_KEY = 'your_generated_secret_key'
```

**Option 2: Use an environment variable**

Create a `.env` file in the root directory and add the key:

```
SECRET_KEY=your_generated_secret_key
```

Then, ensure `settings.py` is set to load the key from the environment:

```python
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
```

6. **Apply Database Migrations**

Run the following command to apply database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Start the Development Server**

run the development server in seperate terminal:

```bash
python manage.py runserver
```
8. **Run the Application**
   
  **open /html/homepage.html in browser to run the application** 


**check pipfile for all dependencies , change the versions if you want for compatability**
