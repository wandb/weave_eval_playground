import streamlit as st
import weave
from openai import OpenAI
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import plotly.express as px
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize session state
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = []
if 'running_evaluation' not in st.session_state:
    st.session_state.running_evaluation = False
if 'custom_scorers' not in st.session_state:
    st.session_state.custom_scorers = []

# Page config
st.set_page_config(
    page_title="Evaluation Playground",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Prompt Engineering Evaluation Playground")
st.markdown("Evaluate prompts across datasets with LLM-as-judge scoring")

# Initialize Weave and OpenAI
try:
    # Use environment variables
    weave_project = os.getenv("WEAVE_PROJECT", "evaluation-playground")
    if not weave_project:
        raise ValueError("WEAVE_PROJECT environment variable not set")
    
    weave.init(project_name=weave_project)
    client = OpenAI()  # This will use OPENAI_API_KEY from environment
except Exception as e:
    st.error(f"Failed to initialize: {e}")
    st.info("Please ensure OPENAI_API_KEY and WEAVE_PROJECT are set in your .env file or environment")
    st.stop()

# Removed pre-built scorer templates - using only custom scorers

# Available OpenAI models
AVAILABLE_MODELS = [
    "gpt-4o",
    "gpt-4o-mini", 
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "o3-mini",
    "o4-mini",
    "o3"
]

def get_dataset_fields(dataset):
    """Extract field names from dataset rows"""
    if not dataset.rows:
        return []
    first_row = dataset.rows[0]
    return list(first_row.keys())

def find_input_field(fields):
    """Find the most likely input field"""
    for field in ['input', 'example', 'question']:
        if field in fields:
            return field
    return fields[0] if fields else None

def find_ground_truth_field(fields):
    """Find the most likely ground truth field"""
    for field in ['expected', 'answer', 'ground_truth', 'output']:
        if field in fields:
            return field
    return None

@st.cache_data
def list_datasets():
    """List available datasets in the Weave project"""
    try:
        # This is a simplified approach - in production you might want to use Weave's API
        # to properly list datasets
        return ["sample_dataset"]  # Placeholder
    except Exception as e:
        st.error(f"Error listing datasets: {e}")
        return []

def run_prompt_on_example(prompt, model, example_input):
    """Run a single prompt on a single example"""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": str(example_input)}
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content

def score_response(scorer_config, model, input_text, response, ground_truth=None):
    """Score a response using an LLM judge"""
    scorer_prompt = scorer_config['prompt']
    
    # Build the scoring prompt with clear field labels
    scoring_context = f"""Please evaluate the following response based on the criteria provided.

**USER INPUT/QUESTION:**
{input_text}

**MODEL RESPONSE:**
{response}
"""
    
    if ground_truth:
        scoring_context += f"""
**EXPECTED/CORRECT ANSWER:**
{ground_truth}
"""
    
    scoring_context += f"""
**EVALUATION CRITERIA:**
{scorer_prompt}"""
    
    if scorer_config['output_type'] == 'numeric':
        scoring_context += f"\n\n**INSTRUCTIONS:** Provide only a number on the scale {scorer_config.get('scale', '1-10')}. Do not include any other text."
    elif scorer_config['output_type'] == 'boolean':
        scoring_context += "\n\n**INSTRUCTIONS:** Answer only 'true' or 'false'. Do not include any other text."
    
    messages = [
        {"role": "system", "content": "You are an expert evaluator. Provide only the requested output format."},
        {"role": "user", "content": scoring_context}
    ]
    
    response = client.chat.completions.create(
        model=scorer_config.get('model', 'gpt-4o-mini'),
        messages=messages,
        temperature=0
    )
    
    score_text = response.choices[0].message.content.strip().lower()
    
    # Parse the score
    if scorer_config['output_type'] == 'numeric':
        try:
            score = float(score_text.split()[0])
            return score
        except:
            return None
    elif scorer_config['output_type'] == 'boolean':
        if 'true' in score_text:
            return not scorer_config.get('invert', False)
        elif 'false' in score_text:
            return scorer_config.get('invert', False)
        else:
            return None
    else:
        return score_text

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Evaluation name
    st.subheader("Evaluation Name")
    eval_name = st.text_input(
        "Name for this evaluation run", 
        value=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="This name will be used to identify your evaluation in Weave"
    )
    
    # Dataset selection
    st.subheader("1. Select Dataset")
    dataset_ref = st.text_input("Dataset Reference", placeholder="dataset_name:version")
    
    # Prompt configuration
    st.subheader("2. Configure Prompts")
    num_prompts = st.number_input("Number of prompts", min_value=1, max_value=5, value=1)
    
    prompts = []
    for i in range(num_prompts):
        with st.expander(f"Prompt {i+1}"):
            prompt_text = st.text_area(f"Prompt text", key=f"prompt_{i}", 
                                     placeholder="You are a helpful assistant...")
            model = st.selectbox(f"Model", AVAILABLE_MODELS, key=f"model_{i}")
            prompts.append({"text": prompt_text, "model": model})
    
    # Scorer configuration
    st.subheader("3. Configure Scorers")
    
    # Get all scorers from session state
    selected_scorers = st.session_state.custom_scorers.copy()
    
    st.write("**Scorers**")
    
    # Display existing custom scorers
    if st.session_state.custom_scorers:
        for idx, scorer in enumerate(st.session_state.custom_scorers):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"✓ {scorer['name']} ({scorer['output_type']})")
            with col2:
                if st.button("Remove", key=f"remove_custom_{idx}"):
                    st.session_state.custom_scorers.pop(idx)
                    st.rerun()
    
    with st.expander("Add Custom Scorer"):
        custom_name = st.text_input("Scorer name")
        custom_prompt = st.text_area("Scorer prompt")
        custom_output = st.selectbox("Output type", ["numeric", "boolean", "text"])
        custom_model = st.selectbox("Model", AVAILABLE_MODELS, key="custom_model")
        
        custom_scale = None
        if custom_output == "numeric":
            custom_scale = st.text_input("Scale (e.g., 1-5)", value="1-10")
        
        if st.button("Add Custom Scorer"):
            if custom_name and custom_prompt:
                custom_config = {
                    "name": custom_name,
                    "prompt": custom_prompt,
                    "output_type": custom_output,
                    "model": custom_model
                }
                if custom_output == "numeric" and custom_scale:
                    custom_config["scale"] = custom_scale
                st.session_state.custom_scorers.append(custom_config)
                st.success(f"Added {custom_name}")
                st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Evaluation Control")
    
    if st.button("🎮 Run Evaluation", type="primary", disabled=st.session_state.running_evaluation):
        if not dataset_ref:
            st.error("Please specify a dataset reference")
        elif not any(p['text'] for p in prompts):
            st.error("Please configure at least one prompt")
        elif not selected_scorers:
            st.error("Please select at least one scorer")
        else:
            st.session_state.running_evaluation = True
            st.rerun()

with col2:
    status_placeholder = st.empty()
    if st.session_state.running_evaluation:
        status_placeholder.info("🔄 Evaluation in progress...")

# Run evaluation
if st.session_state.running_evaluation:
    try:
        # Load dataset
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Loading dataset...")
        dataset = weave.ref(dataset_ref).get()
        
        # Find fields
        fields = get_dataset_fields(dataset)
        input_field = find_input_field(fields)
        ground_truth_field = find_ground_truth_field(fields)
        
        if not input_field:
            st.error("Could not find input field in dataset")
            st.session_state.running_evaluation = False
            st.stop()
        
        # Initialize evaluation logger
        eval_logger = weave.EvaluationLogger(
            name=eval_name,
            model=f"evaluation_playground_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            dataset=dataset_ref
        )
        
        # Progress tracking
        total_steps = len(dataset.rows) * len([p for p in prompts if p['text']])
        current_step = 0
        
        # Results container
        results_container = st.container()
        
        # Run evaluations
        all_results = []
        
        for prompt_idx, prompt_config in enumerate(prompts):
            if not prompt_config['text']:
                continue
                
            prompt_results = []
            
            for example_idx, example in enumerate(dataset.rows):
                current_step += 1
                progress_bar.progress(current_step / total_steps)
                status_text.text(f"Running prompt {prompt_idx+1} on example {example_idx+1}/{len(dataset.rows)}")
                
                # Get input and ground truth
                input_text = example.get(input_field, "")
                ground_truth = example.get(ground_truth_field) if ground_truth_field else None
                
                # Run prompt
                response = run_prompt_on_example(
                    prompt_config['text'],
                    prompt_config['model'],
                    input_text
                )
                
                # Log prediction
                pred_logger = eval_logger.log_prediction(
                    inputs={"prompt": prompt_config['text'], "input": input_text},
                    output=response
                )
                
                # Score with each scorer
                scores = {}
                for scorer in selected_scorers:
                    score = score_response(scorer, scorer['model'], input_text, response, ground_truth)
                    scores[scorer['name']] = score
                    pred_logger.log_score(scorer=scorer['name'], score=score)
                
                pred_logger.finish()
                
                # Store results
                result = {
                    "prompt_idx": prompt_idx,
                    "example_idx": example_idx,
                    "input": input_text,
                    "response": response,
                    "scores": scores,
                    "ground_truth": ground_truth
                }
                prompt_results.append(result)
                all_results.append(result)
                
                # Display live results
                with results_container:
                    st.write(f"**Example {example_idx+1}**")
                    st.write(f"Input: {input_text[:100]}...")
                    st.write(f"Response: {response[:100]}...")
                    st.write(f"Scores: {scores}")
                    st.divider()
        
        # Log summary
        eval_logger.log_summary()
        
        # Store results
        st.session_state.evaluation_results = all_results
        st.session_state.running_evaluation = False
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Show completion status and Weave link
        st.success("✅ Evaluation complete!")
        
        # Get W&B entity from environment or use default
        wandb_entity = os.getenv("WANDB_ENTITY", "your-entity")
        weave_url = f"https://wandb.ai/{wandb_entity}/{weave_project}/weave/evaluations"
        
        st.info(f"📊 View your evaluation results in Weave: [{weave_url}]({weave_url})")
        
        st.balloons()
        
        # Use a small delay before rerun to ensure UI updates are visible
        import time
        time.sleep(0.5)
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during evaluation: {e}")
        st.session_state.running_evaluation = False
        # Use a small delay before rerun
        import time
        time.sleep(0.5)
        st.rerun()

# Results visualization
if st.session_state.evaluation_results:
    st.header("📊 Results")
    
    # Convert to DataFrame for analysis
    df_results = pd.DataFrame(st.session_state.evaluation_results)
    
    # Aggregate scores
    st.subheader("Score Summary")
    
    scorer_names = list(st.session_state.evaluation_results[0]['scores'].keys())
    
    for scorer_name in scorer_names:
        scores = [r['scores'][scorer_name] for r in st.session_state.evaluation_results if r['scores'][scorer_name] is not None]
        
        if scores:
            if isinstance(scores[0], bool):
                true_pct = sum(scores) / len(scores) * 100
                st.metric(f"{scorer_name} (True %)", f"{true_pct:.1f}%")
            elif isinstance(scores[0], (int, float)):
                avg_score = sum(scores) / len(scores)
                st.metric(f"{scorer_name} (Average)", f"{avg_score:.2f}")
            else:
                st.metric(f"{scorer_name}", "Text responses - no aggregate")
    
    # Detailed results table
    st.subheader("Detailed Results")
    
    # Create a simplified view
    display_data = []
    for result in st.session_state.evaluation_results:
        row = {
            "Prompt": f"Prompt {result['prompt_idx']+1}",
            "Example": result['example_idx']+1,
            "Input": result['input'][:50] + "...",
            "Response": result['response'][:50] + "..."
        }
        row.update(result['scores'])
        display_data.append(row)
    
    st.dataframe(pd.DataFrame(display_data))
    
    # Visualizations
    st.subheader("Score Distributions")
    
    for scorer_name in scorer_names:
        scores = [r['scores'][scorer_name] for r in st.session_state.evaluation_results if r['scores'][scorer_name] is not None]
        
        if scores and isinstance(scores[0], (int, float)):
            fig = px.histogram(x=scores, title=f"{scorer_name} Distribution", nbins=20)
            st.plotly_chart(fig, use_container_width=True) 
