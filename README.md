# 🎯 Evaluation Playground

A Streamlit-based application for evaluating prompts across datasets using LLM-as-judge scoring, integrated with Weights & Biases Weave for tracking and visualization.

## Features

- **Multi-Prompt Testing**: Configure and test multiple prompts simultaneously
- **Model Selection**: Choose from various OpenAI models for each prompt
- **Dataset Integration**: Load existing datasets from W&B Weave
- **Custom LLM-as-Judge Scoring**: Define your own scorers using LLMs for evaluation
- **Real-time Progress**: Watch evaluations run with live progress updates
- **Comprehensive Results**: View aggregated scores and detailed results
- **Weave Integration**: All evaluations are logged to W&B Weave using EvaluationLogger
- **Named Evaluations**: Give each evaluation run a custom name for easy tracking

## Setup

### Prerequisites

1. Python 3.9+
2. OpenAI API key
3. Weights & Biases account with Weave access

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd eval_playground
```

2. Install dependencies:

**Using uv (recommended):**
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

**Using pip:**
```bash
pip install -r requirements.txt
```

3. Set environment variables:

Create a `.env` file in the project root:
```bash
# Copy the example and edit with your values
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key
WEAVE_PROJECT=your-weave-project-name
WANDB_ENTITY=your-wandb-username-or-team
EOF
```

Or set them in your shell:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export WEAVE_PROJECT="your-weave-project-name"
export WANDB_ENTITY="your-wandb-username-or-team"
```

### Running the App

**Using uv:**
```bash
uv run streamlit run app.py
```

**Using pip:**
```bash
streamlit run app.py
```

## Usage

### 1. Name Your Evaluation

Give your evaluation run a custom name (defaults to timestamp-based name). This helps you identify and track different experiments in Weave.

### 2. Dataset Selection

Enter a Weave dataset reference in the format `dataset_name:version`. The app will automatically detect input fields (`input`, `example`, or `question`) and ground truth fields (`expected`, `answer`, `ground_truth`, or `output`).

### 3. Configure Prompts

- Add up to 5 different prompts
- Select a model for each prompt
- Each prompt will be evaluated on every example in the dataset

### 4. Configure Scorers

Define custom scorers with:
- **Name**: A descriptive name for your scorer
- **Prompt**: The evaluation criteria and instructions
- **Output type**: 
  - Numeric (with custom scale, e.g., 1-5 or 1-10)
  - Boolean (true/false)
  - Text (free-form response)
- **Model**: Which OpenAI model to use for scoring

You can add multiple scorers and remove them as needed.

### 5. Run Evaluation

Click "Run Evaluation" to:
1. Load the dataset from Weave
2. Run each prompt on every example
3. Score each response using your configured scorers
4. Log all results to Weave with your custom evaluation name

### 6. View Results

**In the App:**
- **Score Summary**: Aggregated metrics for each scorer
  - Numeric scores: Average
  - Boolean scores: True percentage
  - Text scores: No aggregation
- **Detailed Results**: Table view of all evaluations
- **Score Distributions**: Histograms for numeric scores

**In Weave:**
- After evaluation completes, click the provided link to view detailed results in the Weave UI
- Compare evaluations, analyze trends, and share results with your team

## How Scoring Works

Each scorer receives:
- **USER INPUT/QUESTION**: The input from the dataset
- **MODEL RESPONSE**: The generated response from your prompt
- **EXPECTED/CORRECT ANSWER**: The ground truth (if available in dataset)
- **EVALUATION CRITERIA**: Your custom scoring prompt

This structured format helps LLM judges provide more accurate and consistent scores.

## Architecture

The app uses:
- **Streamlit** for the UI
- **OpenAI API** for generating responses and scoring
- **W&B Weave** for dataset management and evaluation logging
- **Plotly** for visualizations
- **python-dotenv** for environment management

## Tips

- Start with a small dataset to test your prompts quickly
- Use descriptive evaluation names to track different experiments
- Create consistent scorer configurations for comparing across evaluations
- Save useful scorer prompts for reuse in future evaluations
- Check the Weave UI link after each evaluation for detailed analysis

## Troubleshooting

- **"Failed to initialize"**: Check that your environment variables are set correctly in `.env`
- **"Could not find input field"**: Ensure your dataset has fields named `input`, `example`, or `question`
- **Scoring errors**: Some responses may fail to parse; these will show as `None` in results
- **UI not updating**: The app will automatically refresh after evaluation completes

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `WEAVE_PROJECT`: Your W&B Weave project name (required)
- `WANDB_ENTITY`: Your W&B username or team name (required for Weave links)

## Future Enhancements

- Dataset browsing UI
- Prompt template variables
- Batch evaluation scheduling
- Export results to CSV
- Save/load scorer configurations
- Comparison view for multiple evaluations
