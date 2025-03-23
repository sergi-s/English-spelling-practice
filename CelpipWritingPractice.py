import os
import json
import time
import openai
import tempfile
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import hashlib

def setup_openai():
    load_dotenv()  # Load API key from .env file
    """Set up OpenAI API with user's API key."""
    print("\n=== CELPIP Writing Practice Tool ===\n")
    if not os.getenv("OPENAI_API_KEY"):
        api_key = input("Please enter your OpenAI API key: ")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key
    print("OpenAI API connection established!\n")

def get_celpip_task_description(task_type):
    """Return the description for a specific CELPIP writing task."""
    tasks = {
        "1": {
            "name": "Writing an Email",
            "description": "You need to write an email (about 150-200 words) in response to a given situation.",
            "format": "- Start with an appropriate greeting\n- Clear introduction stating your purpose\n- 2-3 body paragraphs with details\n- Polite conclusion\n- Appropriate sign-off",
            "time_limit": 27  # minutes
        },
        "2": {
            "name": "Responding to Survey Questions",
            "description": "You need to write a response (about 250-300 words) to survey questions on an everyday topic.",
            "format": "- Introduction stating your overall position\n- 2-3 body paragraphs with detailed explanations\n- Each paragraph should focus on one main point\n- Clear conclusion summarizing your position",
            "time_limit": 33  # minutes
        }
    }
    return tasks.get(task_type)

def get_sample_prompt(task_type):
    """Return a sample prompt for the selected task type."""
    prompts = {
        "1": [  # Email prompts
            "You recently purchased a laptop online that arrived with damage. Write an email to the customer service department describing the problem and requesting a solution.",
            "Your apartment building has been experiencing maintenance issues. Write an email to your landlord explaining the problems and suggesting possible solutions.",
            "You saw an advertisement for a job that interests you, but some information was missing. Write an email requesting additional details about the position."
        ],
        "2": [  # Survey response prompts
            "A local community center is conducting a survey about improving public transportation. Write about the current transportation system, its advantages and disadvantages, and suggest improvements.",
            "A survey asks for your opinion on whether online education is as effective as traditional classroom learning. Discuss your views with reasons and examples.",
            "A neighborhood survey asks for your thoughts on the proposal to convert a vacant lot into either a park or a shopping center. Explain your preference with supporting reasons."
        ]
    }
    import random
    return random.choice(prompts.get(task_type, []))

def load_history():
    """Load history of previously generated prompts."""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if os.path.exists("data/prompt_history.json"):
        try:
            with open("data/prompt_history.json", "r") as f:
                return json.load(f)
        except:
            return {"task1": [], "task2": []}
    return {"task1": [], "task2": []}

def save_to_history(task_type, prompt):
    """Save a prompt to history."""
    history = load_history()
    task_key = f"task{task_type}"
    
    # Create a hash of the prompt to identify similar ones
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    
    if task_key not in history:
        history[task_key] = []
        
    if prompt_hash not in history[task_key]:
        history[task_key].append(prompt_hash)
        
    with open("data/prompt_history.json", "w") as f:
        json.dump(history, f)

def generate_ai_prompt(task_type, history=None):
    """Generate a new prompt using AI based on the task type."""
    task_info = get_celpip_task_description(task_type)
    history = load_history() if history is None else history
    
    # Extract just the prompts from history to pass to the AI
    previous_prompts = []
    if os.path.exists("data"):
        for filename in os.listdir("data"):
            if filename.startswith(f"celpip_task{task_type}_") and filename.endswith(".json"):
                try:
                    with open(os.path.join("data", filename), "r") as f:
                        data = json.load(f)
                        if "prompt" in data:
                            previous_prompts.append(data["prompt"])
                except:
                    pass
    
    # Format the previous prompts for the AI
    previous_prompts_text = ""
    if previous_prompts:
        previous_prompts_text = "PREVIOUSLY USED PROMPTS (DO NOT GENERATE SIMILAR ONES):\n"
        for i, prompt in enumerate(previous_prompts, 1):
            previous_prompts_text += f"{i}. {prompt}\n"
    
    system_prompt = f"""
    You are a CELPIP exam creator. Create a realistic, challenging, and unique prompt for CELPIP Writing Task {task_type}: {task_info['name']}.
    
    Task description: {task_info['description']}
    
    Requirements:
    1. Create a prompt that feels authentic to the CELPIP exam
    2. The scenario should be realistic and relatable
    3. The prompt should allow for demonstration of complex vocabulary
    4. DO NOT create anything similar to the previously used prompts
    5. Return ONLY the prompt text with no additional explanation or commentary
    
    {previous_prompts_text}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # "gpt-3.5-turbo" "gpt-4o-mini" "gpt-4-mini"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a unique CELPIP Writing Task {task_type} prompt."}
            ],
            temperature=0.8,
            max_tokens=300
        )
        new_prompt = response.choices[0].message.content.strip()
        
        # Check if too similar to existing prompts
        prompt_hash = hashlib.md5(new_prompt.encode()).hexdigest()
        task_key = f"task{task_type}"
        
        if task_key in history and prompt_hash in history[task_key]:
            # If similar prompt found, try again with higher temperature
            return generate_ai_prompt(task_type, history)
        
        save_to_history(task_type, new_prompt)
        return new_prompt
    except Exception as e:
        return f"Error generating prompt: {str(e)}"

def start_timer(minutes):
    """Start a countdown timer for the task."""
    seconds = minutes * 60
    print(f"\nTimer started: {minutes} minutes. Start writing now!")
    print("(The timer will run in the background while you write.)")
    return time.time() + seconds

def check_timer(end_time):
    """Check if time has expired."""
    return time.time() >= end_time

def save_response(task_type, prompt, response, feedback):
    """Save the writing practice session to a file."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/celpip_task{task_type}_{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task_type": task_type,
        "prompt": prompt,
        "user_response": response,
        "feedback": feedback
    }
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"\nYour practice session has been saved to {filename}")

def get_ai_feedback(prompt, user_response, task_type):
    """Get OpenAI's feedback on the user's writing."""
    task_desc = get_celpip_task_description(task_type)
    
    system_prompt = f"""
    You are a CELPIP writing examiner and tutor. Analyze the following {task_desc['name']} response 
    for a CELPIP Writing Task {task_type}.
    
    Provide detailed feedback on:
    1. Vocabulary (highlighting good word choices and suggesting more complex alternatives)
    2. Format and Structure (checking against CELPIP requirements)
    3. Grammar and Spelling corrections
    4. Content Development and Coherence
    5. Overall Band Score estimation (out of 12)
    
    Then provide an improved version that would score higher, using more sophisticated vocabulary and 
    better formatting while maintaining the original meaning.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # "gpt-3.5-turbo" "gpt-4o-mini" "gpt-4-mini"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"PROMPT: {prompt}\n\nUSER'S RESPONSE:\n{user_response}"}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting feedback: {str(e)}"

def use_text_editor(prompt, task_info, end_time):
    """Open the user's preferred text editor and return the written content."""
    # Create a temporary file with the prompt at the top
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as temp_file:
        temp_file_name = temp_file.name
        
        # Write the prompt and instructions to the file
        temp_file.write(f"CELPIP WRITING TASK: {task_info['name']}\n")
        temp_file.write(f"TIME LIMIT: {task_info['time_limit']} minutes\n")
        temp_file.write("-" * 50 + "\n\n")
        temp_file.write(f"PROMPT: {prompt}\n\n")
        temp_file.write("-" * 50 + "\n\n")
        temp_file.write("# Write your response below this line. Save and exit when finished.\n")
        temp_file.write("# Your response will be automatically submitted when you exit the editor.\n\n")
    
    # Determine which editor to use
    editor = os.environ.get("EDITOR", "vim")  # Default to vim if no EDITOR env variable
    
    try:
        # Start the editor process
        print(f"\nOpening {editor}. Write your response and exit when done.")
        print(f"Time remaining: {int((end_time - time.time()) / 60)} minutes.")
        
        editor_process = subprocess.Popen([editor, temp_file_name])
        
        # Monitor time while editor is open
        while editor_process.poll() is None:  # While the editor is still running
            if check_timer(end_time):
                print("\nTime's up! Giving you 1 more minute to finish...")
                time.sleep(60)  # Give one extra minute to save and exit
                if editor_process.poll() is None:
                    print("\nForcing editor to close...")
                    editor_process.terminate()
                break
            time.sleep(5)  # Check every 5 seconds
        
        # Read the content from the temp file
        with open(temp_file_name, "r") as f:
            content = f.read()
        
        # Extract just the user's response (remove prompt and instructions)
        lines = content.split("\n")
        response_start = 0
        for i, line in enumerate(lines):
            if "# Write your response below this line." in line:
                response_start = i + 2  # Skip the instruction line and the blank line
                break
        
        user_response = "\n".join(lines[response_start:])
        
        # Clean up the temp file
        os.unlink(temp_file_name)
        
        return user_response
    
    except Exception as e:
        print(f"Error using text editor: {str(e)}")
        # Clean up the temp file in case of error
        if os.path.exists(temp_file_name):
            os.unlink(temp_file_name)
        return ""

def main():
    """Main function to run the CELPIP writing practice tool."""
    setup_openai()
    
    print("Welcome to the CELPIP Writing Practice Tool!")
    print("This tool will help you practice for the CELPIP writing tasks with AI feedback.\n")
    
    while True:
        print("\nCELPIP Writing Tasks:")
        print("1. Task 1: Writing an Email")
        print("2. Task 2: Responding to Survey Questions")
        print("3. Generate New Exam Prompts")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ")
        
        if choice == "4":
            print("Thank you for using the CELPIP Writing Practice Tool. Goodbye!")
            break
        
        if choice == "3":
            # Generate new exam prompts
            print("\n=== Generate New Exam Prompts ===")
            gen_choice = input("Which task type would you like to generate prompts for (1 or 2)? ")
            
            if gen_choice not in ["1", "2"]:
                print("Invalid choice. Please select 1 or 2.")
                continue
            
            num_prompts = input("How many prompts would you like to generate? ")
            try:
                num_prompts = int(num_prompts)
                if num_prompts <= 0 or num_prompts > 10:
                    print("Please enter a number between 1 and 10.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
            
            print(f"\nGenerating {num_prompts} new exam prompts for Task {gen_choice}...")
            
            for i in range(num_prompts):
                print(f"\nPrompt {i+1}:")
                prompt = generate_ai_prompt(gen_choice)
                print(prompt)
                print("\n" + "-"*50)
            
            continue
        
        if choice not in ["1", "2"]:
            print("Invalid choice. Please select 1, 2, 3, or 4.")
            continue
        
        task_info = get_celpip_task_description(choice)
        if not task_info:
            print("Invalid task selection.")
            continue
        
        print(f"\n=== {task_info['name']} ===")
        print(task_info['description'])
        print("\nExpected format:")
        print(task_info['format'])
        print(f"\nTime limit: {task_info['time_limit']} minutes")
        
        prompt_choice = input("\nChoose prompt source:\n1. Sample prompt\n2. Generate AI prompt\n3. Enter your own\nChoice (1-3): ")
        
        if prompt_choice == "1":
            prompt = get_sample_prompt(choice)
            print(f"\nPrompt: {prompt}")
        elif prompt_choice == "2":
            print("\nGenerating a unique AI prompt...")
            prompt = generate_ai_prompt(choice)
            print(f"\nPrompt: {prompt}")
        else:
            prompt = input("\nEnter your own prompt: ")
        
        ready = input("\nAre you ready to begin? (y/n): ").lower()
        if ready != "y":
            continue
        
        end_time = start_timer(task_info['time_limit'])
        
        # Use text editor for response
        user_response = use_text_editor(prompt, task_info, end_time)
        
        time_remaining = max(0, end_time - time.time())
        if time_remaining > 0:
            print(f"\nYou finished with {int(time_remaining / 60)} minutes and {int(time_remaining % 60)} seconds remaining.")
        else:
            print("\nTime's up!")
        
        word_count = len(user_response.split())
        
        print(f"\nYou wrote {word_count} words.")
        
        if choice == "1" and word_count < 150:
            print("Note: Task 1 typically requires 150-200 words. Your response is shorter than recommended.")
        elif choice == "2" and word_count < 250:
            print("Note: Task 2 typically requires 250-300 words. Your response is shorter than recommended.")
        
        print("\nGetting AI feedback on your writing... (this may take a moment)")
        feedback = get_ai_feedback(prompt, user_response, choice)
        
        print("\n=== FEEDBACK ===")
        print(feedback)
        
        save_response(choice, prompt, user_response, feedback)
        
        another = input("\nWould you like to practice another task? (y/n): ").lower()
        if another != "y":
            print("Thank you for using the CELPIP Writing Practice Tool. Goodbye!")
            break

if __name__ == "__main__":
    main()