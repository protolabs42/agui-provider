import { createStore } from "/js/AlpineStore.js";

export const store = createStore("aguiProvider", {
    // Server state
    running: false,
    port: 8401,
    url: "",
    activeRuns: [],
    activeRunCount: 0,
    config: null,

    // UI state
    starting: false,
    stopping: false,
    message: null,
    pollTimer: null,

    init() {},

    async onOpen() {
        await this.refresh();
        this._startPolling();
    },

    cleanup() {
        this._stopPolling();
    },

    // ── Status ──

    async refresh() {
        try {
            const resp = await this._api("status", { action: "status" });
            this.running = resp.running || false;
            this.port = resp.port || 8401;
            this.url = resp.url || "";
            this.activeRuns = resp.active_runs || [];
            this.activeRunCount = resp.active_run_count || 0;
            this.config = resp.config || null;
        } catch (e) {
            console.error("[agui] status check failed:", e);
        }
    },

    // ── Controls ──

    async start() {
        this.starting = true;
        this.message = null;
        try {
            const resp = await this._api("status", { action: "start" });
            if (resp.ok) {
                this.running = true;
                this.url = resp.url || "";
                this.message = { type: "success", text: "AG-UI server started" };
                await this.refresh();
            } else {
                this.message = { type: "error", text: resp.error || "Failed to start" };
            }
        } catch (e) {
            this.message = { type: "error", text: e.message };
        }
        this.starting = false;
    },

    async stop() {
        if (!confirm("Stop the AG-UI server? Active connections will be dropped.")) return;
        this.stopping = true;
        this.message = null;
        try {
            const resp = await this._api("status", { action: "stop" });
            if (resp.ok) {
                this.running = false;
                this.activeRuns = [];
                this.activeRunCount = 0;
                this.config = null;
                this.message = { type: "info", text: "AG-UI server stopped" };
            }
        } catch (e) {
            this.message = { type: "error", text: e.message };
        }
        this.stopping = false;
    },

    // ── Polling ──

    _startPolling() {
        this._stopPolling();
        this.pollTimer = setInterval(() => this.refresh(), 5000);
    },

    _stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    },

    // ── Helpers ──

    async _api(endpoint, body) {
        const { callJsonApi } = await import("/js/api.js");
        return await callJsonApi(`plugins/agui-provider/${endpoint}`, body);
    },
});
