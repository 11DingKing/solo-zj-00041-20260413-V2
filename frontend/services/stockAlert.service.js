import axios from 'axios'
import API_URL from 'services'
import { getToken } from 'Utils/token'

const getAuthHeaders = () => {
    const token = getToken()
    return token ? { Authorization: `Token ${token}` } : {}
}

export const getStockAlertsCount = () => {
    return axios.get(API_URL + 'stock-alerts/count/', {
        headers: getAuthHeaders()
    }).then(res => res.data)
}

export const getPendingStockAlerts = () => {
    return axios.get(API_URL + 'stock-alerts/pending/', {
        headers: getAuthHeaders()
    }).then(res => res.data)
}

export const getAllStockAlerts = (params = {}) => {
    return axios.get(API_URL + 'stock-alerts/', {
        headers: getAuthHeaders(),
        params
    }).then(res => res.data)
}

export const getStockAlertById = (id) => {
    return axios.get(API_URL + `stock-alerts/${id}/`, {
        headers: getAuthHeaders()
    }).then(res => res.data)
}

export const resolveStockAlert = (id) => {
    return axios.post(API_URL + `stock-alerts/${id}/resolve/`, {}, {
        headers: getAuthHeaders()
    }).then(res => res.data)
}

export const sendAlertEmail = (id) => {
    return axios.post(API_URL + `stock-alerts/${id}/send_email/`, {}, {
        headers: getAuthHeaders()
    }).then(res => res.data)
}

export const getInventoryLogsByProduct = (productId) => {
    return axios.get(API_URL + `inventory-logs/by_product/?product_id=${productId}`, {
        headers: getAuthHeaders()
    }).then(res => res.data)
}

export const updateProductStock = (productId, data) => {
    return axios.post(API_URL + `products/${productId}/update-stock/`, data, {
        headers: getAuthHeaders()
    }).then(res => res.data)
}
