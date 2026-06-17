/**
 * WebSocket + REST hook for real-time notifications.
 * Connects to notification-service WS, loads initial unread count via REST.
 */
import { useEffect, useRef } from 'react'
import { useAuthStore, useNotificationStore } from '@/store'
import { notificationService } from '@/services/notificationService'
import type { Notification } from '@/types'

export function useNotifications() {
  const { user } = useAuthStore()
  const { addNotification, setWsConnected, setNotifications, setUnreadCount } = useNotificationStore()
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!user?.id) return

    // Load initial notifications via REST
    notificationService.list(user.id, 1, 50).then((res) => {
      setNotifications(res.data)
      setUnreadCount(res.data.filter((n) => !n.is_read).length)
    }).catch(() => {})

    function connect() {
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/${user!.id}`
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setWsConnected(true)
        // Heartbeat every 30s
        const ping = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          } else {
            clearInterval(ping)
          }
        }, 30_000)
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'notification') {
            const notif: Notification = {
              id: msg.id,
              title: msg.title,
              body: msg.body,
              severity: msg.severity,
              is_read: false,
              is_delivered: true,
              created_at: msg.created_at,
            }
            addNotification(notif)
          }
        } catch {
          // ignore malformed messages
        }
      }

      ws.onclose = () => {
        setWsConnected(false)
        // Reconnect after 5s
        reconnectTimerRef.current = setTimeout(connect, 5_000)
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      wsRef.current?.close()
      setWsConnected(false)
    }
  }, [user?.id])
}
