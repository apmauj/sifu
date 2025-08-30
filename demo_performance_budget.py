#!/usr/bin/env python3
"""
Demo script para mostrar cómo usar el sistema de Performance Budgets
"""
from performance_budget import get_performance_budget_manager

def main():
    print("🚀 DEMO: Sistema de Performance Budgets y Alertas")
    print("=" * 60)

    # Crear manager sin monitoring automático para demo
    manager = get_performance_budget_manager(enable_monitoring=False, enable_alerts=False)

    # Mostrar budgets configurados
    print("\n📊 BUDGETS DE PERFORMANCE CONFIGURADOS:")
    budgets = manager.get_all_budgets()
    for name, budget in budgets.items():
        print(f"• {name}")
        print(f"  📝 {budget['description']}")
        print(f"  🎯 Target: {budget['target_value']}")
        print(f"  ⚠️  Warning: {budget['warning_value']}")
        print(f"  🚨 Critical: {budget['critical_value']}")
        print()

    # Mostrar estado actual
    print("📈 ESTADO ACTUAL DE BUDGETS:")
    status = manager.get_budget_status()
    for name, budget_status in status.items():
        status_icon = "✅" if budget_status['status'] == 'healthy' else "⚠️" if budget_status['status'] == 'warning' else "🚨"
        print(f"{status_icon} {name}: {budget_status['status'].upper()}")
        print(f"   Current: {budget_status['current']:.2f} | Target: {budget_status['target']:.2f}")
        print()

    # Mostrar métricas de throughput
    print("⚡ MÉTRICAS DE THROUGHPUT:")
    throughput = manager.get_throughput_metrics()
    print(f"• Requests/Minute: {throughput['requests_per_minute']}")
    print(f"• Requests/Hour: {throughput['requests_per_hour']}")
    print(f"• Peak RPM: {throughput['peak_rpm']}")
    print()

    print("🎯 DEMO COMPLETADA")
    print("Para usar en producción, habilita monitoring=True y alerts=True")

if __name__ == "__main__":
    main()
