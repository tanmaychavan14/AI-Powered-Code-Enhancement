

async function fetchUser() {
    const response = await axios.get("https://jsonplaceholder.typicode.com/users/1");
    // Bug fix: Explicitly check if response.data is null or undefined
    if (response.data === null || response.data === undefined) {
        throw new TypeError("User data is missing or invalid.");
    }
    return response.data.name;
}


