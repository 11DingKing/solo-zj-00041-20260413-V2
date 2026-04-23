import { useEffect } from 'react';
import Link from 'next/link';
import { useDispatch, useSelector } from 'react-redux';
import { fetchStockAlertsCount } from 'store/modules/stockAlerts';

const StockAlertBadge = () => {
    const dispatch = useDispatch();
    const { pendingCount, loading } = useSelector((state) => state.stockAlerts);
    const { accessToken } = useSelector((state) => state.auth);

    useEffect(() => {
        if (accessToken) {
            dispatch(fetchStockAlertsCount());
        }
    }, [dispatch, accessToken]);

    if (!accessToken) {
        return null;
    }

    return (
        <Link href="/admin/stock-alerts" className="relative mx-2 sm:mx-4">
            <div className="flex items-center cursor-pointer hover:text-orange-500 transition-all">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                </svg>
                {pendingCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
                        {pendingCount > 99 ? '99+' : pendingCount}
                    </span>
                )}
            </div>
        </Link>
    );
};

export default StockAlertBadge;
