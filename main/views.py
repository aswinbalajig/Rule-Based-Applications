from django.shortcuts import render ,get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from . import models
import re
import json
# Create your views here.

class Node:
    def __init__(self, node_type, left=None, right=None, value=None, node_id=None):
        self.node_type = node_type  # "operator" or "operand"
        self.left = left            # Reference to left child (Node)
        self.right = right          # Reference to right child (Node)
        self.value = value          # Value for operand nodes 
        self.node_id = node_id or id(self)  # Unique identifier for each node



def ast_to_json(node):
    if node is None:
        return None

    # Base case: Leaf node (operand)
    if node.node_type == 'operand':
        return {
            'node_type': node.node_type,
            'value': node.value
        }

    # Recursive case: Operator node (AND/OR)
    return {
        'node_type': node.node_type,
        'value': node.value,
        'left': ast_to_json(node.left),   # Recursively serialize the left child
        'right': ast_to_json(node.right)  # Recursively serialize the right child
    }

def create_rule(rule_str):
    tokens = re.findall(r"[\w']+|[()=><]|<=|>=", rule_str)
    print(tokens)
    stack = []
    operators = ['AND', 'OR'] 

    def create_operator_node(operator):
        # Pop two operands (or subtrees) from the stack and create a new operator node
        right = stack.pop()
        left = stack.pop()
        return Node(node_type='operator', left=left, right=right, value=operator)
    
    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == '(':
            # Start of a new sub-expression, just push it to the stack
            stack.append(token)
        elif token == ')':
            # Closing parenthesis means we need to pop until we find a matching '('
            sub_expr = []
            while stack and stack[-1] != '(':
                sub_expr.append(stack.pop())
            try:
                stack.pop()  # Remove '('
            except Exception:
                raise ValueError(f"Invalid grouping of paranthesis") 

            sub_expr.reverse()  # The sub_expr list will have nodes in reverse order

            # Now process the sub-expression (contains a full expression like AND, OR)
            while len(sub_expr) > 1:
                left = sub_expr.pop(0)
                operator = sub_expr.pop(0).value
                right = sub_expr.pop(0)
                stack.append(Node(node_type='operator', left=left, right=right, value=operator))
        elif token in operators:
            # Push the operator to the stack
            stack.append(Node(node_type='operator', value=token))
        else:
            # Process an operand
            try:
                operand = token
                if i + 2 < len(tokens) and tokens[i + 1] in ['=', '>', '<' , '<=' , '>=']:
                    operator = tokens[i + 1]
                    comparison_value = tokens[i + 2]
                    operand = f"{token} {operator} {comparison_value}"
                    i += 2  # Skips over the operator and comparison value
                    stack.append(Node(node_type='operand', value=operand))
                else:
                    # Invalid rule format, raise an error
                    raise ValueError(f"Invalid rule format at token '{token}': expected a comparison operator and value.")
            except ValueError as error:
                return {'valid':False , 'content':str(error)}


        i += 1

    # After processing all tokens, the stack should contain the complete AST
    while len(stack) > 1:
        right = stack.pop()
        operator = stack.pop().value
        left = stack.pop()
        stack.append(Node(node_type='operator', left=left, right=right, value=operator))

    rootnode = stack[0]  # The last item on the stack is the root of the AST
    ast_dict = ast_to_json(rootnode)
    return {'valid':True,'content':json.dumps(ast_dict, indent=4)}



def deserialize_ast(json_data):
    if not json_data:
        return None
    
    # Creates a node based on the current JSON object
    node = Node(
        node_type=json_data['node_type'],
        value=json_data['value']
    )

    # If the node is an operator, recursively creating its left and right children
    if node.node_type == 'operator':
        node.left = deserialize_ast(json_data.get('left'))
        node.right = deserialize_ast(json_data.get('right'))
    
    return node

def evaluate_condition(condition, data):
    # Split the condition (e.g., "age > 30")
    print(f"Evaluating condition: {condition}")
    
    parts = condition.split()
    if len(parts) != 3:
        raise ValueError(f"Invalid condition format: {condition}")
    field, operator, value = parts
    value = value.strip("'")  # Removing  quotes if any (for string comparisons)
    
    # Retrieving the corresponding value from input data
    if field not in data:
        raise ValueError(f"Field '{field}' not present in input data")

    # Converting the data value to the appropriate type for comparison
    data_value = data[field]
    
    # Evaluate the condition based on the operator
    if operator == '>':
        return data_value > int(value)
    elif operator == '<':
        return data_value < int(value)
    elif operator == '<=':
        return data_value <= int(value)
    elif operator == '>=':
        return data_value >= int(value)
    elif operator == '=':
        return str(data_value) == value  # string comparison for equality
    
    else:
        raise ValueError(f"Unsupported operator: {operator}")

# Function to evaluate the AST tree recursively
def evaluate_ast(node, data):
    if node is None:
        return None
    if node.node_type == 'operand':
        # Leaf node: evaluate the condition
        return evaluate_condition(node.value, data)
    elif node.node_type == 'operator':
        # Internal node: recursively evaluate the left and right subtrees
        left_result = evaluate_ast(node.left, data)
        
        
        # Combine the results based on the operator
        if node.value == 'AND':
            if not left_result:
                return False
            right_result = evaluate_ast(node.right, data)
            return left_result and right_result
        elif node.value == 'OR':
            if left_result:
                return True
            right_result = evaluate_ast(node.right, data)
            return left_result or right_result
        else:
            raise ValueError(f"Unsupported operator: {node.value}")
    else:
        raise ValueError(f"Invalid node type: {node.node_type}")
    

def is_valid_parentheses(s):
    stack = []
    # Traversing through each character of the string
    for char in s:
        if char == '(':
            # Push opening parenthesis onto the stack
            stack.append(char)
        elif char == ')':
            # Pop the corresponding opening parenthesis if available
            if not stack:
                return False
            stack.pop()
    
    # In the end, the stack should be empty if parentheses are balanced
    if len(stack) != 0:
        raise ValueError("Invalid grouping of brackets")

def remove_redundant_parentheses(rule_str):
    # Pattern to match redundant parentheses wrapping a logical expression
    # For example: ((age > 30 AND department)) -> (age > 30 AND department)
    while True:
        # Removing parentheses that directly surround another set of parentheses
        new_str = re.sub(r'\(\s*\(([^()]+)\)\s*\)', r'(\1)', rule_str)
        if new_str == rule_str:
            break  # Exit loop if no further replacements are made
        rule_str = new_str
    return rule_str

class ruleStoreViewSet(ModelViewSet):
    queryset=models.rules.objects.all()
    serializer_class=serializers.ruleStoreModelSerializer
    def get_serializer_context(self):
        serializer=serializers.ruleStoreModelSerializer(data=self.request.data)
        if serializer.is_valid():
            rule_string=self.request.data.get('rule_string',None)

            # Regular expression to add spaces around operators, parentheses
            formatted_string = re.sub(r'([()><=])', r' \1 ', rule_string)

            # Replace multiple spaces with a single space
            formatted_string = re.sub(r'\s+', ' ', formatted_string).strip()
            try:
                is_valid_parentheses(formatted_string)
                formatted_string=remove_redundant_parentheses(formatted_string)
                data=create_rule(formatted_string)
            except ValueError as e:
                 data = {'valid':False , 'content':str(e)}
            except Exception as e:
                data={'valid':False,'content':str(e)}
            
            '''
            if(data['valid']):
                return {'json_data':data['content']}
            else:
                return Response({'error':data['content']},status=status.HTTP_406_NOT_ACCEPTABLE)

            '''
            return {'data':data ,'rule_string':formatted_string}


class ruleEvaluate(APIView):
    def post(self, request, rule_id):
        try:
            serializer = serializers.ruleEvaluvateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rule_ast = get_object_or_404(models.rules, pk=rule_id).rule_ast
            print(rule_ast)  
            root_node = deserialize_ast(json.loads(rule_ast))
            result = evaluate_ast(root_node, serializer.validated_data['data'])
            return Response({'result': result}, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        
        except KeyError as ke:
            return Response({'error': f"Missing field: {str(ke)}"}, status=status.HTTP_400_BAD_REQUEST)
        '''
        except Exception as e:
            print(e)
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        '''
        
class RuleCombiner:
    def __init__(self, rule_ids):
        self.rule_ids = rule_ids
        self.rules = self._retrieve_rules_by_ids()

    def _retrieve_rules_by_ids(self):
        # Fetches rules from the database by their IDs and deserialize the AST
        rules_ast = []
        for rule_id in self.rule_ids:
            rule = get_object_or_404(models.rules, pk=rule_id)
            rule_ast = deserialize_ast(json.loads(rule.rule_ast))
            rules_ast.append(rule_ast)
        return rules_ast

    def _find_frequent_operator(self):
        # Counts the frequency of 'AND' and 'OR' operators in the AST
        operator_count = {"AND": 0, "OR": 0}
        for rule_ast in self.rules:
            self._count_operators(rule_ast, operator_count)
        return "AND" if operator_count["AND"] > operator_count["OR"] else "OR"

    def _count_operators(self, node, operator_count):
        if node.node_type == "operator":
            operator_count[node.value] += 1
            if node.left:
                self._count_operators(node.left, operator_count)
            if node.right:
                self._count_operators(node.right, operator_count)

    def _merge_rules(self, frequent_operator):
        # Starts with the first rule and combine the rest one by one
        combined_ast = self.rules[0]  # Start with the first AST
        combined_rule_string = models.rules.objects.get(pk=self.rule_ids[0]).rule_string
        for i in range(1, len(self.rules)):
            new_root = Node(node_type="operator", value=frequent_operator)
            new_root.left = combined_ast  # Left subtree is the current combined AST
            new_root.right = self.rules[i]  # Right subtree is the next rule's AST
            combined_ast = new_root
            current_rule_string=models.rules.objects.get(pk=self.rule_ids[i]).rule_string
            combined_rule_string = f"({combined_rule_string} {frequent_operator} ({current_rule_string}))"

        return combined_ast,combined_rule_string

    def combine_rules(self):
        frequent_operator = self._find_frequent_operator()
        print(f'frequent_operator:{frequent_operator}')  # Get the most frequent operator
        combined_ast,combined_rule_string = self._merge_rules(frequent_operator)  # Merges rules
        return combined_ast,combined_rule_string


class CombineRules(APIView):
    def post(self,request):
        serializer = serializers.ruleCombineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rule_ids=serializer.validated_data['ids']
        rule_name=serializer.validated_data['rule_name']

    #try:
        # Initialize the RuleCombiner and combine rules
        combiner=RuleCombiner(rule_ids)
        combined_ast,combined_rule_string=combiner.combine_rules()
            # Serialize the combined AST to JSON
        combined_rule_ast_json=json.dumps(ast_to_json(combined_ast), indent=4)

    # Create a new rule in the database with the combined AST
        new_rule = models.rules.objects.create(
            rule_name=rule_name,
            rule_string=combined_rule_string,
            rule_ast=combined_rule_ast_json
        )

        return Response({"new_rule_id": new_rule.id}, status=status.HTTP_201_CREATED)

    # except Exception as e:
    #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            

        

               
