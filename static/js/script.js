document.getElementById('start-camera-btn').addEventListener('click', function() {
    fetch('/start_camera')
        .then(response => {
            if (response.ok) {
                console.log('Camera started successfully');
                startVideoStream(); // Apelăm funcția pentru a începe fluxul video
            } else {
                console.error('Failed to start camera');
            }
        })
        .catch(error => console.error('Error:', error));
});

// Funcție pentru a reîmprospăta fluxul video
function startVideoStream() {
    const videoStream = document.getElementById('video-stream');
    videoStream.style.display = 'block'; // Afișează elementul img

    // Setează intervalul de reîmprospătare a imaginii
    setInterval(() => {
        videoStream.src = '/video_feed?' + new Date().getTime(); // Adaugă timestamp pentru a evita caching-ul
    }, 100); // Reîmprospătează la fiecare 100 ms
}
