import { create } from 'zustand';
import type { Notification, WSMessage } from '@/types';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  wsConnected: boolean;
  addNotification: (n: Notification) => void;
  setNotifications: (ns: Notification[]) => void;
  setUnreadCount: (count: number) => void;
  markRead: (id: string) => void;
  markAllRead: () => void;
  setWsConnected: (connected: boolean) => void;
  handleWSMessage: (msg: WSMessage) => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  wsConnected: false,

  addNotification: (n) =>
    set((state) => ({
      notifications: [n, ...state.notifications],
      unreadCount: state.unreadCount + (n.is_read ? 0 : 1),
    })),

  setNotifications: (ns) => set({ notifications: ns }),
  setUnreadCount: (count) => set({ unreadCount: count }),

  markRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, is_read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  markAllRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    })),

  setWsConnected: (connected) => set({ wsConnected: connected }),

  handleWSMessage: (msg) => {
    if (msg.type === 'notification') {
      get().addNotification(msg.payload as Notification);
    }
  },
}));
