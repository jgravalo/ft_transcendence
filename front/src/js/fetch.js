document.getElementById('fetchData').addEventListener('click', function()
//function fetchData()
{
	fetch('http://127.0.0.1:8000/api/my-endpoint/')
		.then(response => response.json())
		.then(data => {
			document.getElementById('output').innerText = JSON.stringify(data);
		})
		.catch(error => console.error('Error:', error));
	});
/*
document.getElementById('fetchData').addEventListener('click', function() {
    const data = { name: 'John' };

    fetch('http://127.0.0.1:8000/api/my-endpoint/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output').innerText = JSON.stringify(data);
    })
    .catch(error => console.error('Error:', error));
});*/
