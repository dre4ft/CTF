

 // Fonction pour afficher les tweets récupérés de l'API
async function renderTweets() {
  const tweetsContainer = document.getElementById('tweets-container');
  
  try {
    // Faire une requête GET à l'API pour obtenir les tweets
    const response = await fetch('/api/tweets');
    const data = await response.json();
    
    // Vérifier si les données sont valides
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des tweets');
    }
    
    // Data est une liste d'objets avec {user, tweet}
    // On va parcourir chaque objet pour afficher le tweet et l'utilisateur
    tweetsContainer.innerHTML = data.map(entry => {
      const user = entry.user;
      const tweet = entry.tweet;
      
      return `
        <div class="tweet">
          <div class="tweet-header">
            <img src="${user.avatar}" alt="${user.full_name}" class="tweet-avatar" />
            <div>
              <div class="tweet-author">${user.full_name}</div>
              <div class="tweet-username">@${user.username}</div>
            </div>
          </div>
          <div class="tweet-content">${tweet.content}</div>
          <div class="tweet-actions">
            <button onclick="likeTweet(${tweet.id})">❤️ ${tweet.likes}</button>
            <button onclick="retweet(${tweet.id})">🔁 ${tweet.retweets}</button>
            <button onclick="shareTweet(${tweet.id})">🔗 Share</button>
          </div>
        </div>
      `;
    }).join('');
  } catch (error) {
    console.error('Erreur lors du chargement des tweets:', error);
    tweetsContainer.innerHTML = '<p>Impossible de récupérer les tweets.</p>';
  }
}
  
  // Fonction pour liker un tweet
async function likeTweet(tweetId) {
  const token = localStorage.getItem('authToken');
  if (token) {
    try {
      // Faire une requête PATCH ou PUT pour mettre à jour les likes du tweet sur le serveur
      const response = await fetch(`/api/tweets/${tweetId}/like`, {
        method: 'PATCH', // ou 'PUT' selon votre API
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'ajout du like');
      }

      // Re-render les tweets après la mise à jour
      renderTweets();
    } catch (error) {
      console.error('Erreur lors de la mise à jour du like:', error);
    }
  }
}

  
// Fonction pour retweeter
async function retweet(tweetId) {
  const token = localStorage.getItem('authToken');
  if (token) {
    try {
      // Faire une requête PATCH ou PUT pour mettre à jour les retweets du tweet sur le serveur
      const response = await fetch(`/api/tweets/${tweetId}/retweet`, {
        method: 'PATCH', // ou 'PUT' selon votre API
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors du retweet');
      }

      // Re-render les tweets après la mise à jour
      renderTweets();
    } catch (error) {
      console.error('Erreur lors de la mise à jour du retweet:', error);
    }
  }
}
  
  // Fonction pour partager un tweet
  function shareTweet(tweetId) {
    const token = localStorage.getItem('authToken');
    if(token){
      const tweet = fakeTweets.find(t => t.id === tweetId);
      alert(`Sharing tweet: "${tweet.content}"`);
    }
  }
  
  // Fonctions pour gérer les modales
  function openLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
  }
  
  function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
  }
  
  function openSignupModal() {
    document.getElementById('signupModal').style.display = 'flex';
  }
  
  function closeSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
  }
  

  // Fermer les modales en cliquant en dehors
  window.onclick = function (event) {
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
  
    if (event.target === loginModal) {
      closeLoginModal();
    }
    if (event.target === signupModal) {
      closeSignupModal();
    }
  };
  
  // Afficher les tweets au chargement de la page
  document.addEventListener('DOMContentLoaded', renderTweets);


// Gestionnaire d'erreurs global
window.onerror = function(message, source, lineno, colno, error) {
    console.error("Erreur JavaScript:", message, "dans", source, "ligne", lineno);
};


function openProfile(){
  const token = localStorage.getItem('authToken');
  const uid = localStorage.getItem('user_id'); 
  if(token && uid){
     window.location.href = `/profile?user_id=${uid}`;
  }
  else{
    openLoginModal();
  }
}

document.getElementById("tweetBox").addEventListener("submit", async function (e) {
  e.preventDefault();

  const currentUser = localStorage.getItem('user_id');
  const token = localStorage.getItem('authToken')
  const tweetBox = document.getElementById("tweetBox");
  const formData = {
        content: tweetBox.querySelector("textarea").value.trim(),
        user_id: localStorage.getItem('user_id')
  };
  if(currentUser){
    if (!formData.content) {
        alert("Le tweet ne peut pas être vide.");
        return;
    }
    
    if (formData.content.length > 280) {
        alert("Le tweet ne peut pas dépasser 280 caractères.");
        return;
    }
    
    try {
      
        const response = await fetch(`http://localhost:6080/api/tweets?content=${encodeURIComponent(formData.content)}&user_id=${formData.user_id}`, {
          method: "POST",
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`HTTP ${response.status} - ${errorData.detail}`);
        }
        
        const result = await response.json();
        this.querySelector("textarea").value = "";
        renderTweets();
        
    } catch (error) {
        console.error("Détails de l'erreur:", error);
        alert(`Erreur lors de l'envoi du tweet: ${error.message}`);
    }
}
else{
  openLoginModal();
}
});




// Modifié : Gestionnaire de connexion
document.getElementById('loginModal').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        username: this.querySelector('[name="username"]').value,
        password: this.querySelector('[name="password"]').value,
        
    };
    try {
        const response = await fetch('http://localhost:6080/api/login', {  // <-- Utiliser l'URL absolue
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();  // 🔹 Lire le message d'erreur
            throw new Error(`HTTP ${response.status} - ${errorData.detail}`);
        }
        const { authToken, user_id } = await response.json();
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('user_id', user_id);
        window.location.href = `/profile?user_id=${user_id}`;
       
        
    } catch (error) {
        console.error("Détails de l'erreur:", error);
        alert(`Erreur de connexion: ${error.message}`);
    }
});

// Modifiez votre code frontend pour voir exactement ce qui est envoyé
document.getElementById('signupModal').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  // Récupérer les données du formulaire
  const formData = {
      username: this.querySelector('[name="username"]').value,
      password: this.querySelector('[name="password"]').value,
      email: this.querySelector('[name="email"]').value,
      full_name: this.querySelector('[name="full_name"]').value
  };


  try {
      const response = await fetch('http://localhost:6080/api/register', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
          },
          body: JSON.stringify(formData)
      });

      if (!response.ok) {
          const errorData = await response.json();
          // Améliorer l'affichage de l'erreur
          throw new Error(JSON.stringify(errorData));
      }
      const result = await response.json();
      alert(`Compte créé avec succès ! ID: ${result.user_id}`);
      closeSignupModal();
  } catch (error) {
      console.error("Erreur d'inscription détaillée:", error);
      alert(error.message);
  }
});
