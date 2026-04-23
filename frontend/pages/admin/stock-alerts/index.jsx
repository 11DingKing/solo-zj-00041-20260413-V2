import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { fetchPendingStockAlerts, resolveAlert, sendEmailAlert, fetchStockAlertsCount } from 'store/modules/stockAlerts';

const StockAlertsPage = () => {
    const router = useRouter();
    const dispatch = useDispatch();
    const { pendingAlerts, loading, pendingCount } = useSelector((state) => state.stockAlerts);
    const { accessToken } = useSelector((state) => state.auth);
    const [filter, setFilter] = useState('pending');
    const [notification, setNotification] = useState(null);

    useEffect(() => {
        if (!accessToken) {
            router.push('/auth/login');
            return;
        }
        dispatch(fetchPendingStockAlerts());
    }, [dispatch, accessToken, router]);

    const showNotification = (message, type = 'success') => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 3000);
    };

    const handleResolve = async (alertId) => {
        try {
            await dispatch(resolveAlert(alertId)).unwrap();
            dispatch(fetchStockAlertsCount());
            showNotification('Alert resolved successfully');
        } catch (error) {
            showNotification('Failed to resolve alert', 'error');
        }
    };

    const handleSendEmail = async (alertId) => {
        try {
            await dispatch(sendEmailAlert(alertId)).unwrap();
            showNotification('Email sent successfully');
        } catch (error) {
            showNotification('Failed to send email', 'error');
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    if (!accessToken) {
        return null;
    }

    return (
        <div className="container mx-auto px-4 py-8 mt-20">
            {notification && (
                <div className={`fixed top-24 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
                    notification.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                }`}>
                    {notification.message}
                </div>
            )}

            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">Stock Alerts</h1>
                    <p className="text-gray-600 mt-2">
                        {pendingCount > 0 ? (
                            <span className="text-red-500 font-semibold">
                                {pendingCount} pending alert{pendingCount !== 1 ? 's' : ''}
                            </span>
                        ) : (
                            <span className="text-green-500">No pending alerts</span>
                        )}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setFilter('pending')}
                        className={`px-4 py-2 rounded-lg transition-all ${
                            filter === 'pending'
                                ? 'bg-red-500 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                    >
                        Pending
                    </button>
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-4 py-2 rounded-lg transition-all ${
                            filter === 'all'
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                    >
                        All
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center items-center py-20">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
            ) : pendingAlerts && pendingAlerts.length > 0 ? (
                <div className="grid gap-4">
                    {pendingAlerts.map((alert) => (
                        <div
                            key={alert.id}
                            className="bg-white rounded-xl shadow-md p-6 border-l-4 border-red-500 hover:shadow-lg transition-shadow"
                        >
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="text-xl font-semibold text-gray-800">
                                            {alert.product_name || 'Unknown Product'}
                                        </h3>
                                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                                            {alert.status}
                                        </span>
                                        {alert.email_sent && (
                                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                                Email Sent
                                            </span>
                                        )}
                                    </div>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                        <div>
                                            <span className="text-gray-500">Current Stock:</span>
                                            <span className="ml-2 font-semibold text-red-600">
                                                {alert.current_stock}
                                            </span>
                                        </div>
                                        <div>
                                            <span className="text-gray-500">Threshold:</span>
                                            <span className="ml-2 font-semibold text-gray-700">
                                                {alert.threshold}
                                            </span>
                                        </div>
                                        <div>
                                            <span className="text-gray-500">Created:</span>
                                            <span className="ml-2 text-gray-700">
                                                {formatDate(alert.created_at)}
                                            </span>
                                        </div>
                                        {alert.last_change_log && (
                                            <div>
                                                <span className="text-gray-500">Last Change:</span>
                                                <span className="ml-2 text-gray-700">
                                                    {alert.last_change_log.change_type} ({alert.last_change_log.quantity})
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    <Link
                                        href={`/admin/stock-alerts/${alert.id}`}
                                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                                    >
                                        View Details
                                    </Link>
                                    {!alert.email_sent && (
                                        <button
                                            onClick={() => handleSendEmail(alert.id)}
                                            className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors text-sm font-medium"
                                        >
                                            Send Email
                                        </button>
                                    )}
                                    <button
                                        onClick={() => handleResolve(alert.id)}
                                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                                    >
                                        Mark Resolved
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-20">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-24 w-24 mx-auto text-green-400 mb-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                    <h2 className="text-2xl font-semibold text-gray-700 mb-2">All Clear!</h2>
                    <p className="text-gray-500">No stock alerts at the moment. All products have sufficient inventory.</p>
                </div>
            )}
        </div>
    );
};

export default StockAlertsPage;
