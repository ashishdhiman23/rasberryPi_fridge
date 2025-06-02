# Smart Fridge API Integration Guide

This guide provides practical examples for integrating your mobile application with the Smart Fridge API.

## Setup and Prerequisites

Before integrating the API into your mobile application, ensure you have:

1. Access to the Smart Fridge API endpoint (`https://smart-fridge-backend.onrender.com/api`)
2. Basic understanding of REST API concepts
3. Appropriate HTTP client library for your mobile platform

## Mobile Integration Examples

### React Native

#### Install dependencies

```bash
npm install axios
# or
yarn add axios
```

#### Setup API Client

```javascript
// src/api/fridgeApi.js
import axios from 'axios';

const API_BASE_URL = 'https://smart-fridge-backend.onrender.com/api';

const fridgeApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add response interceptor for error handling
fridgeApi.interceptors.response.use(
  response => response,
  error => {
    // Handle network errors or server errors
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default fridgeApi;
```

#### Get Fridge Status

```javascript
// src/services/fridgeService.js
import fridgeApi from '../api/fridgeApi';

export const getFridgeStatus = async () => {
  try {
    const response = await fridgeApi.get('/fridge-status');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch fridge status:', error);
    throw error;
  }
};
```

#### Implement Chat with Fridge

```javascript
// src/services/chatService.js
import fridgeApi from '../api/fridgeApi';

export const sendChatMessage = async (message, sessionId = null) => {
  try {
    const response = await fridgeApi.post('/chat', {
      user_message: message,
      session_id: sessionId
    });
    return response.data;
  } catch (error) {
    console.error('Chat API error:', error);
    throw error;
  }
};
```

#### Example Component

```javascript
// src/components/FridgeStatusScreen.js
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, ActivityIndicator } from 'react-native';
import { getFridgeStatus } from '../services/fridgeService';

const FridgeStatusScreen = () => {
  const [fridgeData, setFridgeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadFridgeData = async () => {
      try {
        setLoading(true);
        const data = await getFridgeStatus();
        setFridgeData(data);
        setError(null);
      } catch (err) {
        setError('Failed to load fridge data');
      } finally {
        setLoading(false);
      }
    };

    loadFridgeData();
    
    // Set up polling every 5 minutes
    const intervalId = setInterval(loadFridgeData, 5 * 60 * 1000);
    return () => clearInterval(intervalId);
  }, []);

  if (loading && !fridgeData) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text>Loading Smart Fridge data...</Text>
      </View>
    );
  }

  if (error && !fridgeData) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <Text style={{ color: 'red' }}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold' }}>Smart Fridge Status</Text>
      
      {/* Temperature display */}
      <View style={{ marginVertical: 8 }}>
        <Text>Temperature: {fridgeData?.temp}°C</Text>
        <Text>Humidity: {fridgeData?.humidity}%</Text>
        <Text>Gas Level: {fridgeData?.gas} PPM</Text>
      </View>
      
      {/* Food items list */}
      <Text style={{ fontSize: 16, fontWeight: 'bold', marginTop: 16 }}>Food Items:</Text>
      <FlatList
        data={fridgeData?.items || []}
        renderItem={({ item }) => <Text>• {item}</Text>}
        keyExtractor={(item, index) => `${item}-${index}`}
        ListEmptyComponent={<Text>No food items detected</Text>}
      />
      
      {/* Analysis section */}
      <Text style={{ fontSize: 16, fontWeight: 'bold', marginTop: 16 }}>AI Analysis:</Text>
      <Text>{fridgeData?.analysis?.freshness}</Text>
      <Text>{fridgeData?.analysis?.safety}</Text>
      <Text>{fridgeData?.analysis?.recommendations}</Text>
    </View>
  );
};

export default FridgeStatusScreen;
```

### Swift (iOS)

#### Setup API Client

```swift
// FridgeAPIClient.swift
import Foundation

enum APIError: Error {
    case networkError(Error)
    case dataNotFound
    case jsonParsingError(Error)
    case invalidStatusCode(Int)
}

class FridgeAPIClient {
    private let baseURL = URL(string: "https://smart-fridge-backend.onrender.com/api")!
    private let session = URLSession.shared
    
    // MARK: - Fridge Status
    
    func getFridgeStatus(completion: @escaping (Result<FridgeStatus, APIError>) -> Void) {
        let url = baseURL.appendingPathComponent("fridge-status")
        
        let task = session.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(.networkError(error)))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 0
                completion(.failure(.invalidStatusCode(statusCode)))
                return
            }
            
            guard let data = data else {
                completion(.failure(.dataNotFound))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let fridgeStatus = try decoder.decode(FridgeStatus.self, from: data)
                completion(.success(fridgeStatus))
            } catch let error {
                completion(.failure(.jsonParsingError(error)))
            }
        }
        
        task.resume()
    }
    
    // MARK: - Chat
    
    func sendChatMessage(_ message: String, sessionId: String?, completion: @escaping (Result<ChatResponse, APIError>) -> Void) {
        let url = baseURL.appendingPathComponent("chat")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let chatRequest = ChatRequest(userMessage: message, sessionId: sessionId)
        
        do {
            let encoder = JSONEncoder()
            request.httpBody = try encoder.encode(chatRequest)
        } catch let error {
            completion(.failure(.jsonParsingError(error)))
            return
        }
        
        let task = session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(.networkError(error)))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 0
                completion(.failure(.invalidStatusCode(statusCode)))
                return
            }
            
            guard let data = data else {
                completion(.failure(.dataNotFound))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let chatResponse = try decoder.decode(ChatResponse.self, from: data)
                completion(.success(chatResponse))
            } catch let error {
                completion(.failure(.jsonParsingError(error)))
            }
        }
        
        task.resume()
    }
}
```

#### Data Models

```swift
// FridgeModels.swift
import Foundation

// MARK: - Fridge Status Models

struct FridgeStatus: Codable {
    let temp: Double
    let humidity: Double
    let gas: Int
    let items: [String]
    let priority: [String]?
    let analysis: FridgeAnalysis
    let timestamp: Date
}

struct FridgeAnalysis: Codable {
    let freshness: String
    let safety: String
    let fillLevel: String
    let recommendations: String
    
    enum CodingKeys: String, CodingKey {
        case freshness, safety
        case fillLevel = "fill_level"
        case recommendations
    }
}

// MARK: - Chat Models

struct ChatRequest: Codable {
    let userMessage: String
    let sessionId: String?
    
    enum CodingKeys: String, CodingKey {
        case userMessage = "user_message"
        case sessionId = "session_id"
    }
}

struct ChatResponse: Codable {
    let response: String
    let status: String
    let timestamp: Date
    let sessionId: String?
    
    enum CodingKeys: String, CodingKey {
        case response, status, timestamp
        case sessionId = "session_id"
    }
}
```

#### Example View Controller

```swift
// FridgeStatusViewController.swift
import UIKit

class FridgeStatusViewController: UIViewController {
    
    // UI Outlets
    @IBOutlet weak var temperatureLabel: UILabel!
    @IBOutlet weak var humidityLabel: UILabel!
    @IBOutlet weak var gasLabel: UILabel!
    @IBOutlet weak var itemsTableView: UITableView!
    @IBOutlet weak var analysisTextView: UITextView!
    @IBOutlet weak var activityIndicator: UIActivityIndicatorView!
    
    // Properties
    private let apiClient = FridgeAPIClient()
    private var fridgeStatus: FridgeStatus?
    private var refreshTimer: Timer?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Set up table view
        itemsTableView.dataSource = self
        
        // Initial data fetch
        fetchFridgeStatus()
        
        // Set up refresh timer (every 5 minutes)
        refreshTimer = Timer.scheduledTimer(timeInterval: 300, target: self, selector: #selector(fetchFridgeStatus), userInfo: nil, repeats: true)
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        refreshTimer?.invalidate()
    }
    
    @objc func fetchFridgeStatus() {
        activityIndicator.startAnimating()
        
        apiClient.getFridgeStatus { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                
                switch result {
                case .success(let fridgeStatus):
                    self?.fridgeStatus = fridgeStatus
                    self?.updateUI()
                case .failure(let error):
                    self?.showError(error)
                }
            }
        }
    }
    
    private func updateUI() {
        guard let status = fridgeStatus else { return }
        
        temperatureLabel.text = "\(status.temp)°C"
        humidityLabel.text = "\(status.humidity)%"
        gasLabel.text = "\(status.gas) PPM"
        
        // Update analysis text view
        let analysis = status.analysis
        analysisTextView.text = """
        Freshness: \(analysis.freshness)
        Safety: \(analysis.safety)
        Fill Level: \(analysis.fillLevel)
        Recommendations: \(analysis.recommendations)
        """
        
        itemsTableView.reloadData()
    }
    
    private func showError(_ error: APIError) {
        let message: String
        
        switch error {
        case .networkError:
            message = "Network connection error. Please check your internet connection."
        case .invalidStatusCode(let code):
            message = "Server error with code: \(code)"
        case .dataNotFound:
            message = "Data not found"
        case .jsonParsingError:
            message = "Error parsing response data"
        }
        
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - UITableViewDataSource

extension FridgeStatusViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return fridgeStatus?.items.count ?? 0
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "FoodItemCell", for: indexPath)
        
        if let item = fridgeStatus?.items[indexPath.row] {
            cell.textLabel?.text = item
            
            // Highlight priority items
            if fridgeStatus?.priority?.contains(where: { $0.contains(item) }) ?? false {
                cell.textLabel?.textColor = .red
            } else {
                cell.textLabel?.textColor = .black
            }
        }
        
        return cell
    }
}
```

### Kotlin (Android)

#### Setup with Retrofit

Add to your `build.gradle` (app level):

```groovy
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:okhttp:4.9.1'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.9.1'
}
```

#### API Interface and Models

```kotlin
// FridgeApiService.kt
package com.example.smartfridge.api

import com.example.smartfridge.models.*
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface FridgeApiService {
    @GET("status")
    suspend fun getApiStatus(): Response<ApiStatus>
    
    @GET("fridge-status")
    suspend fun getFridgeStatus(): Response<FridgeStatus>
    
    @POST("chat")
    suspend fun sendChatMessage(@Body request: ChatRequest): Response<ChatResponse>
}
```

```kotlin
// Models.kt
package com.example.smartfridge.models

import com.google.gson.annotations.SerializedName
import java.util.Date

data class ApiStatus(
    val status: String,
    val message: String,
    val timestamp: String,
    @SerializedName("server_info") val serverInfo: ServerInfo
)

data class ServerInfo(
    @SerializedName("render_instance") val renderInstance: String,
    @SerializedName("python_version") val pythonVersion: String
)

data class FridgeStatus(
    val temp: Double,
    val humidity: Double,
    val gas: Int,
    val items: List<String>,
    val priority: List<String>?,
    val analysis: Analysis,
    val timestamp: String
)

data class Analysis(
    val freshness: String,
    val safety: String,
    @SerializedName("fill_level") val fillLevel: String,
    val recommendations: String
)

data class ChatRequest(
    @SerializedName("user_message") val userMessage: String,
    @SerializedName("session_id") val sessionId: String?
)

data class ChatResponse(
    val response: String,
    val status: String,
    val timestamp: String,
    @SerializedName("session_id") val sessionId: String?
)
```

#### API Client Setup

```kotlin
// FridgeApiClient.kt
package com.example.smartfridge.api

import com.example.smartfridge.models.ChatRequest
import com.example.smartfridge.models.ChatResponse
import com.example.smartfridge.models.FridgeStatus
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object FridgeApiClient {
    private const val BASE_URL = "https://smart-fridge-backend.onrender.com/api/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply { 
        level = HttpLoggingInterceptor.Level.BODY 
    }
    
    private val httpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(httpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    private val apiService = retrofit.create(FridgeApiService::class.java)
    
    suspend fun getFridgeStatus(): Response<FridgeStatus> {
        return apiService.getFridgeStatus()
    }
    
    suspend fun sendChatMessage(message: String, sessionId: String? = null): Response<ChatResponse> {
        val request = ChatRequest(userMessage = message, sessionId = sessionId)
        return apiService.sendChatMessage(request)
    }
}
```

#### Repository Pattern Implementation

```kotlin
// FridgeRepository.kt
package com.example.smartfridge.repository

import com.example.smartfridge.api.FridgeApiClient
import com.example.smartfridge.models.ChatResponse
import com.example.smartfridge.models.FridgeStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class FridgeRepository {
    
    suspend fun getFridgeStatus(): Result<FridgeStatus> = withContext(Dispatchers.IO) {
        try {
            val response = FridgeApiClient.getFridgeStatus()
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Empty response body"))
            } else {
                Result.failure(Exception("Error: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun sendChatMessage(message: String, sessionId: String? = null): Result<ChatResponse> = 
        withContext(Dispatchers.IO) {
            try {
                val response = FridgeApiClient.sendChatMessage(message, sessionId)
                if (response.isSuccessful) {
                    response.body()?.let {
                        Result.success(it)
                    } ?: Result.failure(Exception("Empty response body"))
                } else {
                    Result.failure(Exception("Error: ${response.code()} ${response.message()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
}
```

#### ViewModel Implementation

```kotlin
// FridgeStatusViewModel.kt
package com.example.smartfridge.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.smartfridge.models.FridgeStatus
import com.example.smartfridge.repository.FridgeRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit

class FridgeStatusViewModel : ViewModel() {
    
    private val repository = FridgeRepository()
    
    private val _fridgeStatus = MutableLiveData<FridgeStatus>()
    val fridgeStatus: LiveData<FridgeStatus> = _fridgeStatus
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    private var isPolling = false
    
    init {
        loadFridgeStatus()
    }
    
    fun loadFridgeStatus() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            try {
                repository.getFridgeStatus().fold(
                    onSuccess = { 
                        _fridgeStatus.value = it
                        _error.value = null
                    },
                    onFailure = { 
                        _error.value = it.localizedMessage
                    }
                )
            } catch (e: Exception) {
                _error.value = e.localizedMessage
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    fun startPolling() {
        if (isPolling) return
        
        isPolling = true
        viewModelScope.launch {
            while (isPolling) {
                loadFridgeStatus()
                // Polling interval: 5 minutes
                delay(TimeUnit.MINUTES.toMillis(5))
            }
        }
    }
    
    fun stopPolling() {
        isPolling = false
    }
    
    override fun onCleared() {
        super.onCleared()
        stopPolling()
    }
}
```

## Error Handling Best Practices

1. **Network Errors**
   - Implement retry mechanisms for transient network failures
   - Cache data locally for offline access
   - Display meaningful error messages to users

2. **Server Errors (5xx)**
   - Implement exponential backoff for retries
   - Log detailed error information for debugging
   - Provide fallback UI when server is unavailable

3. **Client Errors (4xx)**
   - Validate input data before sending to API
   - Handle authentication/authorization errors gracefully
   - Provide clear guidance to users for resolving the issue

## Caching Strategies

For optimal performance, implement appropriate caching strategies:

1. **In-Memory Cache**
   - Store recent API responses in memory
   - Set appropriate expiration times based on data volatility

2. **Persistent Cache**
   - Use local database (SQLite, Room, Realm) for storing fridge data
   - Implement sync mechanisms to update local data when online

3. **Image Caching**
   - Use image caching libraries for efficient handling of fridge images
   - Implement lazy loading for images in lists

## Monitoring and Debugging

Consider implementing the following for better monitoring:

1. **API Request Logging**
   - Log all API requests and responses (in development)
   - Include timestamps and response times

2. **Error Tracking**
   - Integrate crash reporting tools (Crashlytics, Sentry)
   - Track API failures and user-reported issues

3. **Performance Monitoring**
   - Track API response times
   - Monitor app performance metrics related to API calls

## Testing

Implement thorough testing for your API integration:

1. **Unit Tests**
   - Test repository and API client with mock responses
   - Validate error handling logic

2. **Integration Tests**
   - Test full API interaction flows
   - Validate data mapping and transformation

3. **Mock Server**
   - Use tools like MockWebServer for testing without the real API
   - Simulate various network conditions and response scenarios 