// DOM Elements
const authModal = document.getElementById("authModal");
const closeModal = document.querySelectorAll(".close");
const authTitle = document.getElementById("authTitle");
const switchAuth = document.getElementById("switchAuth");
const authBtn = document.getElementById("authBtn");
const toggleAuthText = document.getElementById("toggleAuth");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const authError = document.getElementById("authError");

const dashboard = document.getElementById("dashboard");
const userNameSpan = document.getElementById("userName");
const goldWalletSpan = document.getElementById("goldWallet");
const buyGoldBtn = document.getElementById("buyGoldBtn");
const refreshBtn = document.getElementById("refreshBtn");

const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

const purchaseModal = document.getElementById("purchaseModal");
const goldAmountInput = document.getElementById("goldAmount");
const purchaseBtn = document.getElementById("purchaseBtn");

// Auth state
let isSignup = false;
let currentUser = {email:"", name:"", goldBalance:0};

// Show auth modal on page load
authModal.style.display = "flex";

// Switch login/signup
switchAuth.addEventListener("click", () => {
    isSignup = !isSignup;
    if(isSignup){
        authTitle.innerText = "Create Account";
        authBtn.innerText = "Sign Up";
        nameInput.style.display = "block";
        toggleAuthText.innerHTML = 'Already have an account? <span id="switchAuth">Login</span>';
    } else {
        authTitle.innerText = "Login";
        authBtn.innerText = "Login";
        nameInput.style.display = "none";
        toggleAuthText.innerHTML = 'Don\'t have an account? <span id="switchAuth">Create Account</span>';
    }
});

// Close modals
closeModal.forEach(el=>el.addEventListener("click",()=>{el.parentElement.parentElement.style.display="none";}));

// Login/Signup handler
authBtn.addEventListener("click", async () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const name = nameInput.value.trim();

    if(!email || !password || (isSignup && !name)){
        authError.innerText = "All fields are required";
        return;
    }

    try{
        const url = isSignup ? "http://localhost:3000/api/signup" : "http://localhost:3000/api/login";
        const body = isSignup ? {email,password,name} : {email,password};
        const res = await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
        const data = await res.json();
        if(res.ok){
            if(isSignup){ alert(data.message); isSignup=false; switchAuth.click(); return; }
            authModal.style.display = "none";
            currentUser = {email:data.email,name:data.name,goldBalance:data.goldBalance};
            userNameSpan.innerText = currentUser.name;
            goldWalletSpan.innerText = currentUser.goldBalance;
            dashboard.classList.remove("hidden");
        } else { authError.innerText = data.error; }
    } catch(err){ authError.innerText = "Server error"; console.error(err);}
});

// Add chat message
const addMessage = (msg, sender) => {
    const div = document.createElement("div");
    div.classList.add("chat-message", sender==="user"?"user-msg":"bot-msg");
    div.innerText = msg;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Send query
const sendQuery = async (query)=>{
    if(!query) return;
    addMessage(query,"user");
    try{
        const res = await fetch("http://localhost:3000/api/query",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({email:currentUser.email,userQuery:query})
        });
        const data = await res.json();
        if(data.redirectToPurchase){ addMessage(data.message,"bot"); purchaseModal.style.display="flex"; }
        else addMessage(data.message,"bot");
    }catch(err){ addMessage("⚠️ Server error","bot"); console.error(err);}
}

// Purchase gold
const purchaseGold = async ()=>{
    const amount = parseFloat(goldAmountInput.value);
    if(!amount || amount<=0) return alert("Enter a valid amount");
    try{
        const res = await fetch("http://localhost:3000/api/purchase-gold",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({email:currentUser.email,amount})
        });
        const data = await res.json();
        addMessage(`✅ ${data.message}`,"bot");
        currentUser.goldBalance = data.updatedGoldBalance;
        goldWalletSpan.innerText = currentUser.goldBalance;
        goldAmountInput.value = "";
        purchaseModal.style.display="none";
    }catch(err){ addMessage("⚠️ Purchase failed","bot"); console.error(err);}
}

// Event listeners
sendBtn.addEventListener("click",()=>{sendQuery(userInput.value.trim()); userInput.value="";});
userInput.addEventListener("keypress", e=>{if(e.key==="Enter") sendBtn.click();});
purchaseBtn.addEventListener("click", purchaseGold);
buyGoldBtn?.addEventListener("click", ()=>{ purchaseModal.style.display = "flex"; });
refreshBtn?.addEventListener("click", async ()=>{
    if(!currentUser.email) return;
    try{
        const res = await fetch(`http://localhost:3000/api/user?email=${encodeURIComponent(currentUser.email)}`);
        const data = await res.json();
        if(data && data.goldBalance!==undefined){
            currentUser.goldBalance = data.goldBalance;
            goldWalletSpan.innerText = currentUser.goldBalance;
        }
    }catch(e){ console.error(e); }
});

// Dynamic grams update
goldAmountInput.addEventListener("input",()=>{
    const amount = parseFloat(goldAmountInput.value);
    if(!amount) return;
    fetch("http://localhost:3000/api/gold-price").then(res=>res.json()).then(data=>{
        const grams = (amount/data.pricePerGram).toFixed(5);
        document.querySelector(".modal-content h3").innerText=`💎 Purchase Digital Gold - ${grams} g`;
    });
});
