# Mobile App Integration Guide for Smart Fridge API

This guide provides detailed instructions for iOS and Android developers to integrate with the Smart Fridge API system.

## Getting Started

### Base URL
All API calls should use the following base URL:
```
https://smart-fridge-backend.onrender.com/api
```

### Authentication
The current version of the API does not require authentication. Future versions will implement OAuth2 or API key-based authentication.

## Integration Steps

### 1. Fetch Fridge Status

This endpoint retrieves the current fridge status including temperature, humidity, gas levels, and detected food items.

#### Endpoint
```
GET /fridge-status
```

#### Android Implementation (Kotlin with Retrofit)

```kotlin
// Define API interface
interface SmartFridgeApi {
    @GET("fridge-status")
    suspend fun getFridgeStatus(): Response<FridgeStatusResponse>
}

// Data models
data class FridgeStatusResponse(
    val temp: Float,
    val humidity: Float,
    val gas: Int,
    val items: List<String>,
    val priority: List<String>,
    val analysis: FridgeAnalysis,
    val timestamp: String
)

data class FridgeAnalysis(
    val freshness: String,
    val safety: String,
    val fill_level: String,
    val recommendations: String
)

// API client setup
object RetrofitClient {
    private const val BASE_URL = "https://smart-fridge-backend.onrender.com/api/"
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val api: SmartFridgeApi = retrofit.create(SmartFridgeApi::class.java)
}

// Usage in ViewModel
class FridgeViewModel : ViewModel() {
    private val _fridgeStatus = MutableLiveData<FridgeStatusResponse>()
    val fridgeStatus: LiveData<FridgeStatusResponse> = _fridgeStatus
    
    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage
    
    fun fetchFridgeStatus() {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.api.getFridgeStatus()
                if (response.isSuccessful) {
                    _fridgeStatus.value = response.body()
                } else {
                    _errorMessage.value = "Failed to get fridge status: ${response.code()}"
                }
            } catch (e: Exception) {
                _errorMessage.value = "Error: ${e.message}"
            }
        }
    }
}
```

#### iOS Implementation (Swift with URLSession)

```swift
// Data models
struct FridgeStatus: Decodable {
    let temp: Float
    let humidity: Float
    let gas: Int
    let items: [String]
    let priority: [String]
    let analysis: FridgeAnalysis
    let timestamp: String
}

struct FridgeAnalysis: Decodable {
    let freshness: String
    let safety: String
    let fill_level: String
    let recommendations: String
}

// API service
class FridgeApiService {
    static let shared = FridgeApiService()
    private let baseURL = "https://smart-fridge-backend.onrender.com/api"
    
    func getFridgeStatus(completion: @escaping (Result<FridgeStatus, Error>) -> Void) {
        let urlString = "\(baseURL)/fridge-status"
        guard let url = URL(string: urlString) else {
            completion(.failure(NSError(domain: "Invalid URL", code: 0)))
            return
        }
        
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                completion(.failure(NSError(domain: "Invalid response", code: (response as? HTTPURLResponse)?.statusCode ?? 0)))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: 0)))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let fridgeStatus = try decoder.decode(FridgeStatus.self, from: data)
                completion(.success(fridgeStatus))
            } catch {
                completion(.failure(error))
            }
        }
        
        task.resume()
    }
}

// Usage in ViewModel
class FridgeViewModel: ObservableObject {
    @Published var fridgeStatus: FridgeStatus?
    @Published var errorMessage: String?
    @Published var isLoading = false
    
    func fetchFridgeStatus() {
        isLoading = true
        
        FridgeApiService.shared.getFridgeStatus { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let status):
                    self?.fridgeStatus = status
                case .failure(let error):
                    self?.errorMessage = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
}
```

### 2. Chat with the Fridge AI

This endpoint allows the user to send messages to the AI assistant to ask questions about fridge contents, get recipe suggestions, or inquire about food safety.

#### Endpoint
```
POST /chat
```

#### Request Body
```json
{
  "user_message": "What can I make with the ingredients in my fridge?",
  "session_id": "optional-session-id-for-conversation-tracking"
}
```

#### Android Implementation (Kotlin with Retrofit)

```kotlin
// Add to API interface
interface SmartFridgeApi {
    // ... other endpoints
    
    @POST("chat")
    suspend fun chatWithFridge(@Body request: ChatRequest): Response<ChatResponse>
}

// Data models
data class ChatRequest(
    val user_message: String,
    val session_id: String? = null
)

data class ChatResponse(
    val response: String,
    val status: String,
    val timestamp: String,
    val session_id: String?
)

// Usage in ViewModel
class ChatViewModel : ViewModel() {
    private val _chatResponse = MutableLiveData<ChatResponse>()
    val chatResponse: LiveData<ChatResponse> = _chatResponse
    
    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage
    
    // For tracking conversation
    private var sessionId: String? = null
    
    fun sendMessage(message: String) {
        viewModelScope.launch {
            try {
                val request = ChatRequest(
                    user_message = message,
                    session_id = sessionId
                )
                
                val response = RetrofitClient.api.chatWithFridge(request)
                
                if (response.isSuccessful) {
                    response.body()?.let { chatResponse ->
                        _chatResponse.value = chatResponse
                        // Save session ID for future messages
                        sessionId = chatResponse.session_id
                    }
                } else {
                    _errorMessage.value = "Failed to send message: ${response.code()}"
                }
            } catch (e: Exception) {
                _errorMessage.value = "Error: ${e.message}"
            }
        }
    }
}
```

#### iOS Implementation (Swift with URLSession)

```swift
// Data models
struct ChatRequest: Encodable {
    let user_message: String
    let session_id: String?
}

struct ChatResponse: Decodable {
    let response: String
    let status: String
    let timestamp: String
    let session_id: String?
}

// Add to API service
extension FridgeApiService {
    func sendChatMessage(message: String, sessionId: String? = nil, completion: @escaping (Result<ChatResponse, Error>) -> Void) {
        let urlString = "\(baseURL)/chat"
        guard let url = URL(string: urlString) else {
            completion(.failure(NSError(domain: "Invalid URL", code: 0)))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let chatRequest = ChatRequest(
            user_message: message,
            session_id: sessionId
        )
        
        do {
            let encoder = JSONEncoder()
            request.httpBody = try encoder.encode(chatRequest)
        } catch {
            completion(.failure(error))
            return
        }
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                completion(.failure(NSError(domain: "Invalid response", code: (response as? HTTPURLResponse)?.statusCode ?? 0)))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: 0)))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let chatResponse = try decoder.decode(ChatResponse.self, from: data)
                completion(.success(chatResponse))
            } catch {
                completion(.failure(error))
            }
        }
        
        task.resume()
    }
}

// Usage in ViewModel
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var errorMessage: String?
    @Published var isLoading = false
    
    // For tracking conversation
    private var sessionId: String?
    
    func sendMessage(text: String) {
        // Add user message to the list
        let userMessage = ChatMessage(text: text, isUser: true)
        messages.append(userMessage)
        
        isLoading = true
        
        FridgeApiService.shared.sendChatMessage(message: text, sessionId: sessionId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    // Add AI response to the list
                    let aiMessage = ChatMessage(text: response.response, isUser: false)
                    self?.messages.append(aiMessage)
                    
                    // Save session ID for future messages
                    self?.sessionId = response.session_id
                case .failure(let error):
                    self?.errorMessage = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
}

// Helper model for UI
struct ChatMessage {
    let id = UUID()
    let text: String
    let isUser: Bool
    let timestamp = Date()
}
```

### 3. Upload Sensor Data and Images

This endpoint uploads sensor readings and fridge images. It uses `multipart/form-data` format to handle both JSON data and image files.

#### Endpoint
```
POST /upload/multipart
```

#### Android Implementation (Kotlin with Retrofit)

```kotlin
// Add to API interface
interface SmartFridgeApi {
    // ... other endpoints
    
    @Multipart
    @POST("upload/multipart")
    suspend fun uploadData(
        @Part("data") data: RequestBody,
        @Part image: MultipartBody.Part?
    ): Response<UploadResponse>
}

// Data model
data class UploadResponse(
    val status: String,
    val message: String,
    val timestamp: String,
    val image_processed: Boolean?,
    val food_items: List<String>?,
    val temperature_status: String?
)

// Usage in ViewModel/Repository
class FridgeRepository(private val api: SmartFridgeApi) {
    
    suspend fun uploadSensorData(temperature: Float, humidity: Float, gas: Int, imageUri: Uri?): Result<UploadResponse> {
        return try {
            // Create JSON data
            val sensorData = JSONObject().apply {
                put("temp", temperature)
                put("humidity", humidity)
                put("gas", gas)
                put("timestamp", SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS", Locale.US)
                    .format(Date()))
            }
            
            val dataRequestBody = sensorData.toString()
                .toRequestBody("application/json".toMediaTypeOrNull())
            
            // Handle optional image
            val imagePart = imageUri?.let { uri ->
                context.contentResolver.openInputStream(uri)?.use { inputStream ->
                    val file = File(context.cacheDir, "fridge_image.jpg")
                    file.outputStream().use { outputStream ->
                        inputStream.copyTo(outputStream)
                    }
                    
                    val requestFile = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
                    MultipartBody.Part.createFormData("image", file.name, requestFile)
                }
            }
            
            val response = api.uploadData(dataRequestBody, imagePart)
            
            if (response.isSuccessful) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Upload failed with code: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

#### iOS Implementation (Swift with URLSession)

```swift
// Add to API service
extension FridgeApiService {
    func uploadSensorData(temperature: Float, humidity: Float, gas: Int, image: UIImage? = nil, completion: @escaping (Result<UploadResponse, Error>) -> Void) {
        let urlString = "\(baseURL)/upload/multipart"
        guard let url = URL(string: urlString) else {
            completion(.failure(NSError(domain: "Invalid URL", code: 0)))
            return
        }
        
        // Create multipart request
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Add sensor data part
        let sensorData: [String: Any] = [
            "temp": temperature,
            "humidity": humidity,
            "gas": gas,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        
        // Convert sensor data to JSON
        guard let jsonData = try? JSONSerialization.data(withJSONObject: sensorData),
              let jsonString = String(data: jsonData, encoding: .utf8) else {
            completion(.failure(NSError(domain: "Failed to serialize data", code: 0)))
            return
        }
        
        // Add JSON data part
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"data\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: application/json\r\n\r\n".data(using: .utf8)!)
        body.append("\(jsonString)\r\n".data(using: .utf8)!)
        
        // Add image part if available
        if let image = image, let imageData = image.jpegData(compressionQuality: 0.8) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"image\"; filename=\"fridge_image.jpg\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
            body.append(imageData)
            body.append("\r\n".data(using: .utf8)!)
        }
        
        // Add closing boundary
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        // Set request body
        request.httpBody = body
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(NSError(domain: "Invalid response", code: 0)))
                return
            }
            
            guard httpResponse.statusCode == 200, let data = data else {
                completion(.failure(NSError(domain: "Server error", code: httpResponse.statusCode)))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let uploadResponse = try decoder.decode(UploadResponse.self, from: data)
                completion(.success(uploadResponse))
            } catch {
                completion(.failure(error))
            }
        }
        
        task.resume()
    }
}

// Response model
struct UploadResponse: Decodable {
    let status: String
    let message: String
    let timestamp: String
    let image_processed: Bool?
    let food_items: [String]?
    let temperature_status: String?
}
```

## Important Implementation Tips

### 1. Handling Cold Start Issues

Since the backend is hosted on Render's free tier, it may sometimes experience "cold starts" when the service hasn't been used for a while. Implement retry logic in your mobile app:

```kotlin
// Android retry logic example
suspend fun <T> retryIO(
    times: Int = 3,
    initialDelay: Long = 1000,
    maxDelay: Long = 10000,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(times - 1) {
        try {
            return block()
        } catch (e: IOException) {
            // Only retry certain exceptions like connection timeouts
        }
        delay(currentDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelay)
    }
    return block() // last attempt
}
```

```swift
// iOS retry logic example
func retry<T>(
    _ operation: @escaping () -> Result<T, Error>,
    attempts: Int = 3,
    delay: TimeInterval = 1.0,
    completion: @escaping (Result<T, Error>) -> Void
) {
    operation().fold(
        onSuccess: { completion(.success($0)) },
        onFailure: { error in
            if attempts > 1 {
                DispatchQueue.global().asyncAfter(deadline: .now() + delay) {
                    retry(operation, attempts: attempts - 1, delay: delay * 2, completion: completion)
                }
            } else {
                completion(.failure(error))
            }
        }
    )
}
```

### 2. Optimizing Image Uploads

Images from the fridge camera can be large. Optimize them before uploading:

```kotlin
// Android image optimization
fun optimizeImage(uri: Uri): File {
    val bitmap = MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
    
    // Resize if too large
    val maxDimension = 1024
    var width = bitmap.width
    var height = bitmap.height
    
    if (width > maxDimension || height > maxDimension) {
        val aspectRatio = width.toFloat() / height.toFloat()
        if (width > height) {
            width = maxDimension
            height = (width / aspectRatio).toInt()
        } else {
            height = maxDimension
            width = (height * aspectRatio).toInt()
        }
    }
    
    val resizedBitmap = Bitmap.createScaledBitmap(bitmap, width, height, true)
    
    // Compress to file
    val file = File(context.cacheDir, "optimized_image.jpg")
    file.outputStream().use { outputStream ->
        resizedBitmap.compress(Bitmap.CompressFormat.JPEG, 85, outputStream)
    }
    
    return file
}
```

```swift
// iOS image optimization
func optimizeImage(_ image: UIImage) -> UIImage {
    let maxDimension: CGFloat = 1024
    
    var width = image.size.width
    var height = image.size.height
    
    if width > maxDimension || height > maxDimension {
        let aspectRatio = width / height
        if width > height {
            width = maxDimension
            height = width / aspectRatio
        } else {
            height = maxDimension
            width = height * aspectRatio
        }
    }
    
    let size = CGSize(width: width, height: height)
    
    UIGraphicsBeginImageContextWithOptions(size, false, 0.0)
    image.draw(in: CGRect(origin: .zero, size: size))
    let optimizedImage = UIGraphicsGetImageFromCurrentImageContext()
    UIGraphicsEndImageContext()
    
    return optimizedImage ?? image
}
```

### 3. Recommended UI Components

#### Android

- Temperature display: Use [MPAndroidChart](https://github.com/PhilJay/MPAndroidChart) for visualizing temperature over time
- Chat interface: [ChatMessageView](https://github.com/bassaer/ChatMessageView) for a WhatsApp-style chat experience
- Food item display: RecyclerView with GridLayoutManager for an efficient grid display

#### iOS

- Temperature display: [Charts](https://github.com/danielgindi/Charts) for visualizing temperature data
- Chat interface: MessageKit for a complete chat UI solution
- Food item display: UICollectionView with a compositional layout for a modern grid experience

## Troubleshooting Common Issues

1. **"Cannot Connect to Server" Error**
   - Check your internet connection
   - The Render free tier may be "warming up" - implement retry logic
   - Verify the base URL is correct

2. **Upload Failures**
   - Ensure your multipart form is correctly formatted
   - Check image size (keep under 5MB)
   - Verify JSON is valid and fields match the expected format

3. **App Crashes During Image Upload**
   - Implement proper memory management for large images
   - Use background threads for network operations
   - Consider using a dedicated image upload library like Glide (Android) or Kingfisher (iOS)

## Best Practices

1. **Use a Proper Network Layer**
   - Android: Retrofit + OkHttp + Kotlin Coroutines
   - iOS: Combine + URLSession or Alamofire

2. **Implement Proper Error Handling**
   - Provide meaningful error messages to users
   - Log errors for debugging
   - Implement retry mechanisms for transient failures

3. **Cache Results When Appropriate**
   - Store recent fridge status for offline access
   - Implement a proper caching strategy for images

4. **Follow MVVM Architecture**
   - Separate UI (View) from business logic (ViewModel)
   - Use LiveData/Flow (Android) or Combine (iOS) for reactive updates

## Support

If you encounter issues with API integration, please contact the development team or create an issue in the GitHub repository with:

1. A detailed description of the problem
2. Steps to reproduce
3. Expected vs. actual behavior
4. Mobile platform and version
5. Code sample demonstrating the issue

---

Last updated: April 29, 2025 