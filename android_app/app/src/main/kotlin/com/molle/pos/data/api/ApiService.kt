package com.molle.pos.data.api

import retrofit2.http.*
import retrofit2.Response

interface ApiService {
    
    // Products
    @GET("products/")
    suspend fun getProducts(): Response<List<ProductResponse>>
    
    @GET("products/by_barcode/")
    suspend fun getProductByBarcode(@Query("barcode") barcode: String): Response<ProductResponse>
    
    @GET("products/low_stock/")
    suspend fun getLowStockProducts(): Response<List<ProductResponse>>
    
    // Sales Invoices
    @GET("sales-invoices/")
    suspend fun getSalesInvoices(): Response<List<SalesInvoiceResponse>>
    
    @GET("sales-invoices/today/")
    suspend fun getTodayInvoices(): Response<List<SalesInvoiceResponse>>
    
    @GET("sales-invoices/statistics/")
    suspend fun getSalesStatistics(): Response<StatisticsResponse>
    
    @POST("sales-invoices/")
    suspend fun createSalesInvoice(@Body invoice: SalesInvoiceRequest): Response<SalesInvoiceResponse>
    
    // Customers
    @GET("customers/")
    suspend fun getCustomers(): Response<List<CustomerResponse>>
    
    // POS Transactions
    @POST("pos-transactions/")
    suspend fun createTransaction(@Body transaction: TransactionRequest): Response<TransactionResponse>
}

// Response Models
data class ProductResponse(
    val id: String,
    val code: String,
    val name_ar: String,
    val name_en: String,
    val barcode: String,
    val cost_price: Double,
    val selling_price: Double,
    val quantity_on_hand: Int,
    val is_active: Boolean
)

data class SalesInvoiceResponse(
    val id: String,
    val invoice_number: String,
    val customer: CustomerResponse,
    val invoice_date: String,
    val status: String,
    val total_amount: Double,
    val items: List<SalesInvoiceItemResponse>
)

data class SalesInvoiceItemResponse(
    val id: String,
    val product: ProductResponse,
    val quantity: Int,
    val unit_price: Double,
    val total_amount: Double
)

data class CustomerResponse(
    val id: String,
    val name: String,
    val email: String,
    val phone: String,
    val balance: Double
)

data class StatisticsResponse(
    val today: TodayStats,
    val month: MonthStats
)

data class TodayStats(
    val total: Double,
    val count: Int
)

data class MonthStats(
    val total: Double,
    val count: Int
)

// Request Models
data class SalesInvoiceRequest(
    val customer_id: String,
    val items: List<SalesInvoiceItemRequest>,
    val notes: String = ""
)

data class SalesInvoiceItemRequest(
    val product_id: String,
    val quantity: Int,
    val unit_price: Double
)

data class TransactionRequest(
    val transaction_type: String,
    val amount: Double,
    val payment_method: String,
    val reference_number: String = ""
)

data class TransactionResponse(
    val id: String,
    val transaction_type: String,
    val amount: Double,
    val payment_method: String,
    val created_at: String
)
