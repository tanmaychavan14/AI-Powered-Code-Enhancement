const axios = require("axios");

async function fetchUser() {
    const response = await axios.get("https://jsonplaceholder.typicode.com/users/1");
    return response.data.name;
}

module.exports = { fetchUser };

// Jest Test Cases
// Mock the axios module to prevent actual API calls during tests
jest.mock("axios");

describe('fetchUser', () => {
    // Clear all mock implementations before each test to ensure test isolation
    beforeEach(() => {
        axios.get.mockClear();
    });

    // Test Case 1: Successfully fetches a user's name
    test('should return the user name on a successful API call', async () => {
        const mockUserData = {
            data: {
                id: 1,
                name: "Leanne Graham",
                username: "Bret",
                email: "Sincere@april.biz",
                address: {
                    street: "Kulas Light",
                    suite: "Apt. 556",
                    city: "Gwenborough",
                    zipcode: "92998-3874",
                    geo: { lat: "-37.3159", lng: "81.1496" }
                },
                phone: "1-770-736-8031 x56442",
                website: "hildegard.org",
                company: {
                    name: "Romaguera-Crona",
                    catchPhrase: "Multi-layered client-server neural-net",
                    bs: "harness real-time e-markets"
                }
            },
        };
        axios.get.mockResolvedValue(mockUserData);

        const userName = await fetchUser();

        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
        expect(userName).toBe("Leanne Graham");
    });

    // Test Case 2: Handles API call failure (e.g., network error, server error)
    test('should throw an error if the API call fails', async () => {
        const errorMessage = "Network Error: Could not connect to API";
        axios.get.mockRejectedValue(new Error(errorMessage));

        await expect(fetchUser()).rejects.toThrow(errorMessage);
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });

    // Test Case 3: Handles response where the 'name' property is missing
    test('should return undefined if the "name" property is missing from the response data', async () => {
        const mockUserDataWithoutName = {
            data: {
                id: 1,
                username: "Bret",
                email: "Sincere@april.biz",
            },
        };
        axios.get.mockResolvedValue(mockUserDataWithoutName);

        const userName = await fetchUser();

        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(userName).toBeUndefined(); // Accessing a non-existent property returns undefined
    });

    // Test Case 4: Handles response where 'data' object itself is null or undefined
    test('should throw a TypeError if response.data is null or undefined', async () => {
        // Scenario A: response.data is null
        axios.get.mockResolvedValue({ data: null });
        await expect(fetchUser()).rejects.toThrow(TypeError);
        await expect(fetchUser()).rejects.toThrow("Cannot read properties of null (reading 'name')");
        expect(axios.get).toHaveBeenCalledTimes(1); // Only one call for the first expect

        axios.get.mockClear(); // Clear mock for the next scenario
        // Scenario B: response.data is undefined (e.g., axios resolved with an empty object)
        axios.get.mockResolvedValue({}); // Effectively makes response.data undefined
        await expect(fetchUser()).rejects.toThrow(TypeError);
        await expect(fetchUser()).rejects.toThrow("Cannot read properties of undefined (reading 'name')");
        expect(axios.get).toHaveBeenCalledTimes(1);
    });

    // Test Case 5: Ensures the correct URL is used for the API call
    test('should call axios.get with the specific user URL', async () => {
        const mockUserData = { data: { name: "Another User" } };
        axios.get.mockResolvedValue(mockUserData);

        await fetchUser();

        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith("https://jsonplaceholder.typicode.com/users/1");
    });

    // Test Case 6: Handles a valid scenario where the user's name is an empty string
    test('should return an empty string if the user name is an empty string', async () => {
        const mockUserData = {
            data: {
                id: 1,
                name: "",
                username: "Bret",
            },
        };
        axios.get.mockResolvedValue(mockUserData);

        const userName = await fetchUser();

        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(userName).toBe("");
    });
});