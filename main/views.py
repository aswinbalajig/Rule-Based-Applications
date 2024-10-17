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
        self.value = value          # Value for operand nodes (optional)
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
            stack.pop()  # Remove '('
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
                if i + 2 < len(tokens) and tokens[i + 1] in ['=', '>', '<']:
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
    field, operator, value = condition.split()
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
    if node.node_type == 'operand':
        # Leaf node: evaluate the condition
        return evaluate_condition(node.value, data)
    elif node.node_type == 'operator':
        # Internal node: recursively evaluate the left and right subtrees
        left_result = evaluate_ast(node.left, data)
        right_result = evaluate_ast(node.right, data)
        
        # Combine the results based on the operator
        if node.value == 'AND':
            return left_result and right_result
        elif node.value == 'OR':
            return left_result or right_result
        else:
            raise ValueError(f"Unsupported operator: {node.value}")
    else:
        raise ValueError(f"Invalid node type: {node.node_type}")
    



class ruleStoreViewSet(ModelViewSet):
    queryset=models.rules.objects.all()
    serializer_class=serializers.ruleStoreModelSerializer
    def get_serializer_context(self):
        serializer=serializers.ruleStoreModelSerializer(data=self.request.data)
        if serializer.is_valid():
            rule_string=self.request.data.get('rule_string',None)
            data=create_rule(rule_string)
            '''
            if(data['valid']):
                return {'json_data':data['content']}
            else:
                return Response({'error':data['content']},status=status.HTTP_406_NOT_ACCEPTABLE)

            '''
            return {'data':data}

class ruleEvaluate(APIView):
    def post(self, request, rule_id):
        try:
            serializer = serializers.ruleEvaluvateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rule_ast = get_object_or_404(models.rules, pk=rule_id).rule_ast  
            root_node = deserialize_ast(rule_ast)
            result = evaluate_ast(root_node, serializer.data)
            return Response({'result': result}, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        
        except KeyError as ke:
            return Response({'error': f"Missing field: {str(ke)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CombineRules(APIView):
    def post(self,request):
        serializer = serializers.ruleCombineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rule_ids=serializer.data
        

               
