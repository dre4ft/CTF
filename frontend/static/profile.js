let currentUser = null;

// Récupère l'ID utilisateur depuis l'URL
function getUserIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('user_id');
}

// Charge les données du profil
async function loadProfile() {
    const token = localStorage.getItem('authToken')
    const userId = getUserIdFromUrl();
    if (!userId) return;

    try {
        const response = await fetch(`http://localhost:6080/api/users/${userId}`,{
            method : 'GET', 
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        const user = await response.json();
        
        document.getElementById('fullName').value = user.full_name || '';
        document.getElementById('email').value = user.email || '';

        // Affiche la section admin si l'utilisateur est admin
        if (user.is_admin) {
            document.querySelector('.admin').style.display = 'block';
        }

        currentUser = user;
    } catch (error) {
        alert('Erreur de chargement du profil');
    }
}

async function displayUserTweet(){
    const tweetsContainer = document.getElementById('container');
    const token = localStorage.getItem('authToken')
    tweetsContainer.innerHTML = "";
    try {
        // Faire une requête GET à l'API pour obtenir les tweets
        const response = await fetch(`/api/tweets/${getUserIdFromUrl()}`,{
            method : 'GET', 
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }}
         );
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération des tweets');
        }
        const data = await response.json();
    
    // Vérifier si les données sont valides
    
    
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




function displayParameter(){
    const profileSection = document.getElementById('container');
    profileSection.innerHTML = "";
    if (!profileSection) {
        console.error("Erreur : tweets-container introuvable !");
        return;
    }
    profileSection.innerHTML = `
            
            <h1>Paramètres du Profil</h1>
            
            <!-- Section Informations Utilisateur -->
            <div class="profile-card">
                <h2>Informations Personnelles</h2>
                <form id="profileForm">
                    <input type="text" id="fullName" placeholder="Nom complet">
                    <input type="email" id="email" placeholder="Email">
                    <button type="submit">Mettre à jour</button>
                </form>
            </div>

            <!-- Section Changement Mot de Passe (VULNÉRABLE) -->
            <div class="profile-card vulnerable">
                <h2>Changer le Mot de Passe</h2>
                <form id="passwordForm">
                    <input type="password" id="newPassword" placeholder="Nouveau mot de passe" required>
                    <button type="submit">Changer le mot de passe</button>
                </form>
               <!-- 💡 Aucune vérification de l'ancien mot de passe nécessaire ! -->
                     
            </div>

            <!-- Section Admin (cachée par défaut) -->
            <div class="profile-card admin" style="display: none;">
                <h2>🔒 Accès Administrateur</h2>
                <button onclick="location.href='/ssh'">Se connecter au Backend</button>
            </div>
        `;
        loadProfile();
        PasswordManager();
}


    // Ce code ne sera exécuté qu'une fois que le DOM est complètement chargé

function PasswordManager(){    // Gestion du formulaire de mot de passe
    const passwordForm = document.getElementById('passwordForm');
    const token = localStorage.getItem('authToken');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newPassword = document.getElementById('newPassword').value;
            
            try {
                const response = await fetch(`/api/users/${getUserIdFromUrl()}/password`, {
                    method: 'PATCH',
                    headers: { 
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        password: newPassword })
                });

                alert('mot de passe changé');
            } catch (error) {
                console.log('Échec du changement de mot de passe',error);
            }
        });
    }
    
}

function goHome(){
    window.location.href = '/';
}

// Vérifie l'authentification au chargement
async function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = '/';
        return;
    }
    await displayUserTweet();;
    
    
}

// Initialisation
document.addEventListener('DOMContentLoaded', checkAuth);
