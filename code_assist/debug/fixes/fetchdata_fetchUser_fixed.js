

async function fetchUser() {
    const response = await axios.get("https://jsonplaceholder.typicode.com/users/1");
    return response.data.name; // <--- This line is problematic if response.data is null

}