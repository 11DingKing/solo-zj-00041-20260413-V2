import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import {
    getStockAlertsCount,
    getPendingStockAlerts,
    getAllStockAlerts,
    getStockAlertById,
    resolveStockAlert,
    sendAlertEmail
} from 'services/stockAlert.service';

export const fetchStockAlertsCount = createAsyncThunk(
    'stockAlerts/fetchStockAlertsCount',
    async () => {
        return await getStockAlertsCount()
    }
)

export const fetchPendingStockAlerts = createAsyncThunk(
    'stockAlerts/fetchPendingStockAlerts',
    async () => {
        return await getPendingStockAlerts()
    }
)

export const fetchAllStockAlerts = createAsyncThunk(
    'stockAlerts/fetchAllStockAlerts',
    async (params = {}) => {
        return await getAllStockAlerts(params)
    }
)

export const fetchStockAlertById = createAsyncThunk(
    'stockAlerts/fetchStockAlertById',
    async (id) => {
        return await getStockAlertById(id)
    }
)

export const resolveAlert = createAsyncThunk(
    'stockAlerts/resolveAlert',
    async (id) => {
        return await resolveStockAlert(id)
    }
)

export const sendEmailAlert = createAsyncThunk(
    'stockAlerts/sendEmailAlert',
    async (id) => {
        return await sendAlertEmail(id)
    }
)

const initialState = {
    pendingCount: 0,
    pendingAlerts: [],
    allAlerts: [],
    currentAlert: null,
    loading: false,
    error: null,
}

export const stockAlertsSlice = createSlice({
    name: 'stockAlerts',
    initialState,
    reducers: {
        clearCurrentAlert: (state) => {
            state.currentAlert = null
        },
        clearError: (state) => {
            state.error = null
        }
    },
    extraReducers: {
        [fetchStockAlertsCount.pending]: (state) => {
            state.loading = true
        },
        [fetchStockAlertsCount.fulfilled]: (state, action) => {
            state.loading = false
            state.pendingCount = action.payload.pending_count || 0
        },
        [fetchStockAlertsCount.rejected]: (state, action) => {
            state.loading = false
            state.error = action.error.message
        },

        [fetchPendingStockAlerts.pending]: (state) => {
            state.loading = true
        },
        [fetchPendingStockAlerts.fulfilled]: (state, action) => {
            state.loading = false
            state.pendingAlerts = action.payload
        },
        [fetchPendingStockAlerts.rejected]: (state, action) => {
            state.loading = false
            state.error = action.error.message
        },

        [fetchAllStockAlerts.pending]: (state) => {
            state.loading = true
        },
        [fetchAllStockAlerts.fulfilled]: (state, action) => {
            state.loading = false
            state.allAlerts = action.payload
        },
        [fetchAllStockAlerts.rejected]: (state, action) => {
            state.loading = false
            state.error = action.error.message
        },

        [fetchStockAlertById.pending]: (state) => {
            state.loading = true
        },
        [fetchStockAlertById.fulfilled]: (state, action) => {
            state.loading = false
            state.currentAlert = action.payload
        },
        [fetchStockAlertById.rejected]: (state, action) => {
            state.loading = false
            state.error = action.error.message
        },

        [resolveAlert.fulfilled]: (state, action) => {
            state.pendingCount = Math.max(0, state.pendingCount - 1)
            state.pendingAlerts = state.pendingAlerts.filter(
                alert => alert.id !== action.payload.id
            )
            if (state.currentAlert?.id === action.payload.id) {
                state.currentAlert = action.payload
            }
        },
    }
})

export const { clearCurrentAlert, clearError } = stockAlertsSlice.actions
export default stockAlertsSlice.reducer
