/** @odoo-module **/
/**
 * GearGuard JavaScript Enhancements
 * ==================================
 * Custom JS for enhanced interactivity
 */

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Dashboard Statistics Component
 * Shows real-time KPIs for maintenance management
 */
export class GearGuardDashboard extends Component {
    static template = "gearguard.Dashboard";
    
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.state = useState({
            totalEquipment: 0,
            activeEquipment: 0,
            scrappedEquipment: 0,
            totalRequests: 0,
            newRequests: 0,
            inProgressRequests: 0,
            overdueRequests: 0,
            repairedThisMonth: 0,
            loading: true,
        });
        
        onWillStart(async () => {
            await this.loadStatistics();
        });
    }
    
    async loadStatistics() {
        try {
            // Equipment stats
            this.state.totalEquipment = await this.orm.searchCount(
                "maintenance.equipment", []
            );
            this.state.activeEquipment = await this.orm.searchCount(
                "maintenance.equipment", [["is_scrap", "=", false]]
            );
            this.state.scrappedEquipment = await this.orm.searchCount(
                "maintenance.equipment", [["is_scrap", "=", true]]
            );
            
            // Request stats
            this.state.totalRequests = await this.orm.searchCount(
                "maintenance.request", []
            );
            this.state.newRequests = await this.orm.searchCount(
                "maintenance.request", [["state", "=", "new"]]
            );
            this.state.inProgressRequests = await this.orm.searchCount(
                "maintenance.request", [["state", "=", "in_progress"]]
            );
            this.state.overdueRequests = await this.orm.searchCount(
                "maintenance.request", [
                    ["is_overdue", "=", true],
                    ["state", "not in", ["repaired", "scrap"]]
                ]
            );
            
            this.state.loading = false;
        } catch (error) {
            console.error("Failed to load GearGuard statistics:", error);
            this.state.loading = false;
        }
    }
    
    openNewRequests() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "New Requests",
            res_model: "maintenance.request",
            view_mode: "kanban,tree,form",
            domain: [["state", "=", "new"]],
        });
    }
    
    openOverdueRequests() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Overdue Requests",
            res_model: "maintenance.request",
            view_mode: "tree,form",
            domain: [
                ["is_overdue", "=", true],
                ["state", "not in", ["repaired", "scrap"]]
            ],
        });
    }
    
    openEquipment() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "All Equipment",
            res_model: "maintenance.equipment",
            view_mode: "kanban,tree,form",
        });
    }
}

GearGuardDashboard.props = {};

// Register the component
registry.category("actions").add("gearguard_dashboard", GearGuardDashboard);
