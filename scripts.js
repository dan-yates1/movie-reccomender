const movies = [
    { id: 1, title: "Movie 1" },
    { id: 2, title: "Movie 2" },
];

const movieList = document.getElementById('movieList');
movies.forEach(movie => {
    const movieElement = document.createElement('div');
    movieElement.innerHTML = `
        ${movie.title}
        <button onclick="rateMovie(${movie.id}, 'like')">Like</button>
        <button onclick="rateMovie(${movie.id}, 'dislike')">Dislike</button>
    `;
    movieList.appendChild(movieElement);
});

function rateMovie(movieId, rating) {
    console.log(`Rated Movie ID: ${movieId} as ${rating}`);
}

function getRecommendations() {
    let data = {
        ratings: [
            { movieId: 1, rating: 5 },
            { movieId: 2, rating: 3 },
        ]
    };

    fetch('http://localhost:8000/recommendations', {
        method: 'POST',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(recommendations => {
            let recommendationsList = document.getElementById('recommendationsList');
            recommendationsList.innerHTML = '';
            recommendations.forEach(movie => {
                recommendationsList.innerHTML += `<p>${movie.title}</p>`;
            });
        })
        .catch(error => {
            console.error("Error fetching recommendations:", error);
        });
}

