import { configureStore } from '@reduxjs/toolkit'
import commonReducer from './modules/common'
import authReducer from './modules/auth'
import productsReducer from './modules/product'
import stockAlertsReducer from './modules/stockAlerts'

export const store = configureStore({
    reducer: {
        'auth': authReducer,
        'common': commonReducer,
        'products': productsReducer,
        'stockAlerts': stockAlertsReducer,
    },
})
