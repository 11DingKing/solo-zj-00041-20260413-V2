import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { fetchStockAlertById, resolveAlert, sendEmailAlert, fetchStockAlertsCount } from 'store/modules/stockAlerts';
import { getInventoryLogsByProduct } from 'services/stockAlert.service';

const StockAlertDetailPage = () => {
    const router = useRouter();
    const { id } = router.query;
    const dispatch = useDispatch();
    const { currentAlert, loading } = useSelector((state) => state.stockAlerts);
    const { accessToken } = useSelector((state) => state.auth);
    const [inventoryLogs, setInventoryLogs] = useState([]);
    const [logsLoading, setLogsLoading] = useState(false);
    const [notification, setNotification] = useState(null);

    useEffect(() => {
        if (!accessToken) {
            router.push('/auth/login');
            return;
        }
        if (id) {
            dispatch(fetchStockAlertById(id));
        }
    }, [dispatch, accessToken, router, id]);

    useEffect(() => {
        if (currentAlert?.product) {
            loadInventoryLogs(currentAlert.product);
        }
    }, [currentAlert]);

    const loadInventoryLogs = async (productId) => {
        setLogsLoading(true);
        try {
            const logs = await getInventoryLogsByProduct(productId);
            setInventoryLogs(Array.isArray(logs) ? logs : []);
        } catch (error) {
            console.error('Failed to load inventory logs:', error);
            setInventoryLogs([]);
        } finally {
            setLogsLoading(false);
        }
    };

    const showNotification = (message, type = 'success') => {
        setNotification({ message, type });
        setTimeout(() => setNotification(null), 3000);
    };

    const handleResolve = async () => {
        if (!currentAlert) return;
        try {
            await dispatch(resolveAlert(currentAlert.id)).unwrap();
            dispatch(fetchStockAlertsCount());
            showNotification('Alert resolved successfully');
        } catch (error) {
            showNotification('Failed to resolve alert', 'error');
        }
    };

    const handleSendEmail = async () => {
        if (!currentAlert) return;
        try {
            await dispatch(sendEmailAlert(currentAlert.id)).unwrap();
            showNotification('Email sent successfully');
        } catch (error) {
            showNotification('Failed to send email', 'error');
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleString();
    };

    const getChangeTypeBadge = (changeType) => {
        const isIncrease = changeType === 'increase';
        return (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                isIncrease ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
                {isIncrease ? '+' : '-'}{changeType}
            </span>
        );
    };

    if (!accessToken) {
        return null;
    }

    if (loading || !currentAlert) {
        return (
            <div className="container mx-auto px-4 py-8 mt-20">
                <div className="flex justify-center items-center py-20">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                </div>
            </div>
        );
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

            <div className="mb-6">
                <Link href="/admin/stock-alerts" className="flex items-center text-blue-500 hover:text-blue-700 transition-colors">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 mr-2"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Alerts
                </Link>
            </div>

            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="bg-gradient-to-r from-red-500 to-orange-500 px-6 py-4">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                            <h1 className="text-2xl font-bold text-white">Stock Alert Details</h1>
                            <p className="text-red-100 mt-1">
                                {currentAlert.product_name || 'Unknown Product'}
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <span className={`px-4 py-2 rounded-lg text-sm font-medium ${
                                currentAlert.status === 'pending'
                                    ? 'bg-red-600 text-white'
                                    : 'bg-green-600 text-white'
                            }`}>
                                {currentAlert.status.toUpperCase()}
                            </span>
                            {currentAlert.email_sent && (
                                <span className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium">
                                    Email Sent
                                </span>
                            )}
                        </div>
                    </div>
                </div>

                <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="bg-gray-50 rounded-lg p-4">
                            <p className="text-sm text-gray-500 mb-1">Product Name</p>
                            <p className="text-lg font-semibold text-gray-800">
                                {currentAlert.product_name || 'N/A'}
                            </p>
                        </div>
                        <div className="bg-red-50 rounded-lg p-4">
                            <p className="text-sm text-gray-500 mb-1">Current Stock</p>
                            <p className="text-2xl font-bold text-red-600">
                                {currentAlert.current_stock}
                            </p>
                        </div>
                        <div className="bg-orange-50 rounded-lg p-4">
                            <p className="text-sm text-gray-500 mb-1">Threshold</p>
                            <p className="text-2xl font-bold text-orange-600">
                                {currentAlert.threshold}
                            </p>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                            <p className="text-sm text-gray-500 mb-1">Created At</p>
                            <p className="text-lg font-semibold text-gray-800">
                                {formatDate(currentAlert.created_at)}
                            </p>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-4 mb-8">
                        {currentAlert.status === 'pending' && (
                            <button
                                onClick={handleResolve}
                                className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
                            >
                                Mark as Resolved
                            </button>
                        )}
                        {!currentAlert.email_sent && (
                            <button
                                onClick={handleSendEmail}
                                className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors font-medium"
                            >
                                Send Email Notification
                            </button>
                        )}
                    </div>

                    <div className="border-t pt-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Inventory Changes</h2>
                        
                        {logsLoading ? (
                            <div className="flex justify-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                            </div>
                        ) : inventoryLogs && inventoryLogs.length > 0 ? (
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="bg-gray-50">
                                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Date</th>
                                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Type</th>
                                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Quantity</th>
                                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Previous Stock</th>
                                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">New Stock</th>
                                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Reason</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200">
                                        {inventoryLogs.slice(0, 10).map((log) => (
                                            <tr key={log.id} className="hover:bg-gray-50">
                                                <td className="px-4 py-3 text-sm text-gray-700">
                                                    {formatDate(log.created_at)}
                                                </td>
                                                <td className="px-4 py-3">
                                                    {getChangeTypeBadge(log.change_type)}
                                                </td>
                                                <td className="px-4 py-3 text-sm font-medium text-gray-700">
                                                    {log.quantity}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-700">
                                                    {log.previous_stock}
                                                </td>
                                                <td className="px-4 py-3 text-sm font-medium text-gray-700">
                                                    {log.new_stock}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-600">
                                                    {log.reason || 'N/A'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                No inventory change logs found for this product.
                            </div>
                        )}
                    </div>

                    {currentAlert.last_change_log && (
                        <div className="border-t pt-6 mt-6">
                            <h2 className="text-xl font-bold text-gray-800 mb-4">Last Change That Triggered This Alert</h2>
                            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div>
                                        <p className="text-sm text-gray-500">Change Type</p>
                                        <p className="font-medium">{currentAlert.last_change_log.change_type}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">Quantity</p>
                                        <p className="font-medium">{currentAlert.last_change_log.quantity}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">Previous Stock</p>
                                        <p className="font-medium">{currentAlert.last_change_log.previous_stock}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">New Stock</p>
                                        <p className="font-medium">{currentAlert.last_change_log.new_stock}</p>
                                    </div>
                                </div>
                                {currentAlert.last_change_log.reason && (
                                    <div className="mt-4">
                                        <p className="text-sm text-gray-500">Reason</p>
                                        <p className="font-medium">{currentAlert.last_change_log.reason}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StockAlertDetailPage;
