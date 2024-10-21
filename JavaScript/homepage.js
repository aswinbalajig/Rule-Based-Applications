let currRulesCount=0;

//add button conditions

 function redirection(from)
 {
     const addRuleLink=document.querySelector('#addrule');
    
     if(from==='combine')
     {
         if(currRulesCount<=1)
         {   window.location.href = addRuleLink.href;
             alert('create more than one rule to combine rules');
             
         }
     }
     else if(from==='evaluate')
     {
         if(currRulesCount<1)
         {   window.location.href = addRuleLink.href;
             alert('create atleast one rule to perform evaluation');
             

         }
     }

 }


//end of add button conditions


//form submit eventlisteners

async function combinerules(event)
{   event.preventDefault();
    const rule_name=document.querySelector('#CombineRuleName').value;
    const ids=[];
    const checkboxes = document.querySelectorAll('input[name="rules"]:checked');
    checkboxes.forEach((checkbox)=>{
        ids.push(checkbox.value);
    });
    console.log(`selected_rules_id : ${ids}`);
    if(ids.length>1){
        try{

            const response=await fetch(`http://127.0.0.1:8000/rules/combine_rules`,
                {
                    method:'POST',
                    headers:{
                        'Content-Type' : 'application/json' 
                    },
                    body : JSON.stringify({rule_name,ids})
                }
            );
    
            if(response.ok)
            {
                alert('rule is successfully created');
                window.location.href="../html/homepage.html"
            }
            else{
                const errorData=await response.json();
                console.error("Unable to Create: ",erroData);
                alert('Unable to Create Rule :'+ errorData.non_field_errors[0]);
            }
    
        }
        catch(error)
        {
            console.error(`Error Creating Rule: ${error}`);
            alert(`Error Creating Rule: ${error}`);
        } 
    }
    else
    {
        alert('Create more than one rule to combine');
    }
    
}




async function createrules(event)
{   event.preventDefault();
    const rule_name=document.getElementById('InputName').value;
    const rule_string=document.getElementById('InputRule').value;
    try{

        const response=await fetch(`http://127.0.0.1:8000/rules/`,
            {
                method:'POST',
                headers:{
                    'Content-Type' : 'application/json' 
                },
                body : JSON.stringify({rule_name,rule_string})
            }
        );

        if(response.ok)
        {
            alert('rule is successfully created');
            window.location.href="../html/homepage.html"
        }
        else{
            const errorData=await response.json();
            console.error("Unable to Create: ",erroData);
            alert('Unable to Create Rule :'+ errorData.non_field_errors[0]);
        }

    }
    catch(error)
    {
        console.error(`Error Creating Rule: ${error}`);
        alert(`Error Creating Rule: ${error}`);
    }
}

async function evaluate(event)
{   event.preventDefault();
    let data=document.getElementById("EvaluationRuleData").value;
    data=JSON.parse(data);
    const rule_id=document.getElementById("ruleslistevaluate").value;
    try{
        const response = await fetch(`http://127.0.0.1:8000/rules/${rule_id}/evaluate`,
            {
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify({data})
            }
        );

        if(response.ok)
        {
            const result=await response.json();
            if(result)
            {
                alert("Condition satisfies");
            }
            else
            {
                alert("Condition does not satisifies");
            }
        }
        else
        {   
            const errorData=await response.json();
            console.error("Unable to Evaluate: ",erroData);
            alert('Unable to Evaluate :'+ errorData.non_field_errors[0]);
        }

    }
    catch(error)
    {
        alert(`Unable to Evaluate : ${error}`);
    }
}
//end of form submit eventlisteners
//display rules
async function fetchrules()
{
    try {
        url='http://127.0.0.1:8000/rules/';
        const response = await fetch(url);
        if(response.ok)
        return await response.json();
        else{console.log(response);
            const errordata=await response.json();
            console.error(`Error : ${errordata.detail}`);}
    } catch (error) {
        console.error('Error fetching Rules:', error);
        alert(`Error fetching Rules: ${error}`);
    }

}

async function displayRules()
{   
    const combineRuleList=document.querySelector('#ruleslistcombine');
    const evaluateRuleList=document.querySelector('#ruleslistevaluate');
    combineRuleList.innerHTML='';
    evaluateRuleList.innerHTML='';
    const rules=await fetchrules();
    currRulesCount=rules.length;
    rules.forEach(
        
        (rule) => 
            {
                const option = document.createElement('option');
                option.value = rule.id;
                option.textContent = rule.rule_name;
                evaluateRuleList.appendChild(option);

                combineRuleList.innerHTML+=`<input class="form-check-input" type="checkbox" value=${rule.id} name="rules">${rule.rule_name}</input>`

            }

    );
}
//end display fetch rules

document.addEventListener('DOMContentLoaded',
    async function()
    {
        displayRules();
        
        //redirection eventlisteners
        document.querySelector('#combinerules').removeEventListener('click',()=>{redirection("combine")});
        document.querySelector('#combinerules').addEventListener('click',()=>{redirection("combine")});
        document.querySelector('#evaluaterules').removeEventListener('click',()=>{redirection("evaluate")});
        document.querySelector('#evaluaterules').addEventListener('click',()=>{redirection("evaluate")});
        //end of redirection event listeners
        //form event listeners
        document.querySelector('#RuleForm').removeEventListener('submit',createrules);
        document.querySelector('#RuleForm').addEventListener('submit',createrules);
        document.querySelector('#CombineRulesForm').removeEventListener('submit',combinerules);
        document.querySelector('#CombineRulesForm').addEventListener('submit',combinerules);
        document.querySelector('#EvaluationForm').removeEventListener('submit',evaluate);
        document.querySelector('#EvaluationForm').addEventListener('submit',evaluate);
        

        //end of form event listeners
    }
);

