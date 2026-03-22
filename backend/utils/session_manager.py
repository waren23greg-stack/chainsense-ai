import os, time, threading, uuid
from middleware.security import safe_join, sha256_file

class SessionManager:
    DEMO = "demo"
    def __init__(self, upload_folder, ttl=3600):
        self.folder   = upload_folder
        self.ttl      = ttl
        self._store   = {}
        self._lock    = threading.RLock()
        self._start_cleanup()

    def create_session(self, filename, file_hash):
        sid = uuid.uuid4().hex[:8]
        with self._lock:
            self._store[sid] = {"session_id": sid, "filename": filename, "file_hash": file_hash, "created_at": time.time(), "last_access": time.time(), "access_count": 0}
        return sid

    def touch(self, sid):
        with self._lock:
            if sid in self._store:
                self._store[sid]["last_access"]  = time.time()
                self._store[sid]["access_count"] += 1

    def get_file_path(self, sid):
        if sid == self.DEMO:
            try:    return safe_join(self.folder, "demo.csv")
            except: return None
        with self._lock:
            meta = self._store.get(sid)
            if not meta or self._expired(meta):
                self._delete(sid)
                return None
        try:
            p = safe_join(self.folder, f"upload_{sid}.csv")
            return p if os.path.isfile(p) else None
        except: return None

    def session_info(self, sid):
        if sid == self.DEMO:
            return {"session_id": "demo", "filename": "supply_chain_demo.csv", "permanent": True}
        with self._lock:
            meta = self._store.get(sid)
            if not meta or self._expired(meta): return None
            return {**meta, "expires_in_seconds": max(0, int(self.ttl - (time.time() - meta["last_access"])))}

    def delete_session(self, sid):
        if sid == self.DEMO: return False
        with self._lock:    return self._delete(sid)

    def active_count(self):
        with self._lock: return len(self._store)

    def _expired(self, meta):
        return (time.time() - meta["last_access"]) > self.ttl

    def _delete(self, sid):
        try:
            p = safe_join(self.folder, f"upload_{sid}.csv")
            if os.path.isfile(p): os.remove(p)
        except: pass
        return self._store.pop(sid, None) is not None

    def _start_cleanup(self):
        def loop():
            while True:
                time.sleep(300)
                with self._lock:
                    expired = [s for s, m in self._store.items() if self._expired(m)]
                    for s in expired: self._delete(s)
                if expired: print(f"[SessionManager] Purged {len(expired)} session(s).")
        threading.Thread(target=loop, daemon=True, name="session-cleanup").start()

_mgr = None
def get_session_manager(upload_folder=None, ttl=3600):
    global _mgr
    if _mgr is None:
        if not upload_folder: raise RuntimeError("SessionManager not initialised.")
        _mgr = SessionManager(upload_folder, ttl)
    return _mgr
