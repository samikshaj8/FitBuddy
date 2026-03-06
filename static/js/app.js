document.addEventListener('DOMContentLoaded', () => {
    const setupForm = document.getElementById('setup-form');
    const setupSection = document.getElementById('setup-section');
    const resultsSection = document.getElementById('results-section');
    const resetBtn = document.getElementById('reset-btn');
    
    const generateBtn = document.getElementById('generate-btn');
    const generateBtnText = generateBtn.querySelector('.btn-text');
    const generateLoader = document.getElementById('generate-loader');
    const setupError = document.getElementById('setup-error');
    
    const feedbackBtn = document.getElementById('feedback-btn');
    const feedbackBtnText = document.getElementById('feedback-btn-text');
    const feedbackLoader = document.getElementById('feedback-loader');
    const feedbackInput = document.getElementById('feedback-text');
    const feedbackError = document.getElementById('feedback-error');
    
    const tipText = document.getElementById('tip-text');
    const planContainer = document.getElementById('plan-container');
    
    let currentUserId = null;
    let currentPlanId = null;

    setupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        setupError.classList.add('hidden');
        setLoading(generateBtnText, generateLoader, true, "Generating Plan...");

        const userData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            weight: parseInt(document.getElementById('weight').value),
            goal: document.getElementById('goal').value,
            intensity: document.getElementById('intensity').value
        };

        try {
            // 1. Create User
            const userResponse = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
            
            if (!userResponse.ok) throw new Error("Failed to create user profile");
            const user = await userResponse.json();
            currentUserId = user.id;

            // 2. Fetch Tip in parallel
            fetchTip(userData.goal);

            // 3. Generate Plan
            const planResponse = await fetch(`/api/generate_plan/${currentUserId}`, {
                method: 'POST'
            });
            
            if (!planResponse.ok) throw new Error("Failed to generate plan");
            const plan = await planResponse.json();
            currentPlanId = plan.id;
            
            // 4. Render
            renderPlan(plan.content);
            
            // 5. Switch Views
            setupSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');

        } catch (error) {
            setupError.textContent = error.message || "An error occurred during generation.";
            setupError.classList.remove('hidden');
        } finally {
            setLoading(generateBtnText, generateLoader, false, "Generate My Plan");
        }
    });

    feedbackBtn.addEventListener('click', async () => {
        const feedback = feedbackInput.value.trim();
        if (!feedback) return;
        
        feedbackError.classList.add('hidden');
        setLoading(feedbackBtnText, feedbackLoader, true, "Updating...");
        
        try {
            const response = await fetch(`/api/feedback/${currentPlanId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plan_id: currentPlanId, text: feedback })
            });
            
            if (!response.ok) throw new Error("Failed to update plan");
            const updatedPlan = await response.json();
            
            renderPlan(updatedPlan.content);
            feedbackInput.value = '';
            
        } catch (error) {
            feedbackError.textContent = error.message || "An error occurred while updating.";
            feedbackError.classList.remove('hidden');
        } finally {
            setLoading(feedbackBtnText, feedbackLoader, false, "Update Plan");
        }
    });

    resetBtn.addEventListener('click', () => {
        setupForm.reset();
        currentUserId = null;
        currentPlanId = null;
        resultsSection.classList.add('hidden');
        setupSection.classList.remove('hidden');
    });

    async function fetchTip(goal) {
        try {
            const response = await fetch('/api/tips/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal: goal })
            });
            if (response.ok) {
                const data = await response.json();
                tipText.textContent = data.tip;
            }
        } catch (error) {
            console.error("Tip fetching failed:", error);
            tipText.textContent = "Stay hydrated and get enough sleep for optimal recovery.";
        }
    }

    function renderPlan(planContent) {
        planContainer.innerHTML = '';
        
        const days = ['day_1', 'day_2', 'day_3', 'day_4', 'day_5', 'day_6', 'day_7'];
        
        days.forEach((dayKey, index) => {
            const dayData = planContent[dayKey];
            if (!dayData) return;
            
            const card = document.createElement('div');
            card.className = 'day-card';
            
            const header = document.createElement('div');
            header.className = 'day-header';
            
            const title = document.createElement('div');
            title.className = 'day-title';
            title.textContent = `Day ${index + 1}`;
            
            const focus = document.createElement('div');
            focus.className = 'day-focus';
            focus.textContent = dayData.focus || "Rest";
            
            header.appendChild(title);
            header.appendChild(focus);
            card.appendChild(header);
            
            const list = document.createElement('ul');
            list.className = 'exercise-list';
            
            const exercises = dayData.exercises || [];
            if (exercises.length === 0) {
                const li = document.createElement('li');
                li.textContent = "Rest day or activity of your choice";
                list.appendChild(li);
            } else {
                exercises.forEach(ex => {
                    const li = document.createElement('li');
                    li.textContent = ex;
                    list.appendChild(li);
                });
            }
            
            card.appendChild(list);
            planContainer.appendChild(card);
        });
    }

    function setLoading(textElement, loaderElement, isLoading, newText) {
        if (isLoading) {
            textElement.textContent = newText;
            loaderElement.classList.remove('hidden');
        } else {
            textElement.textContent = newText;
            loaderElement.classList.add('hidden');
        }
    }
});
