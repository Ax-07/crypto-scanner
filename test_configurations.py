"""
Test des différentes configurations d'indicateurs
Valide que le scanner fonctionne avec tous les modes
"""

import sys
import config
from logger import get_logger
from scanner import scan_market

logger = get_logger()


def test_configuration(test_name, use_rsi, use_ma, description):
    """
    Teste une configuration spécifique

    Args:
        test_name (str): Nom du test
        use_rsi (bool): Activer RSI
        use_ma (bool): Activer MA
        description (str): Description de la config
    """
    print("\n" + "=" * 80)
    print(f"🧪 TEST: {test_name}")
    print(f"📝 Description: {description}")
    print(f"⚙️  Configuration: USE_RSI={use_rsi}, USE_MA={use_ma}")
    print("=" * 80)

    # Modifier la configuration temporairement
    original_rsi = config.USE_RSI
    original_ma = config.USE_MA
    original_max = config.MAX_PAIRS

    config.USE_RSI = use_rsi
    config.USE_MA = use_ma
    config.MAX_PAIRS = 5  # Limiter à 5 paires pour test rapide

    try:
        # Exécuter le scan
        results = scan_market()

        # Afficher les résultats
        if results:
            print(f"\n✅ Test réussi: {len(results)} paire(s) trouvée(s)")

            # Vérifier les colonnes présentes
            if results:
                first_result = results[0]
                print(f"📊 Colonnes présentes: {', '.join(first_result.keys())}")

                # Vérifications
                if use_rsi and 'rsi' not in first_result:
                    print("❌ ERREUR: RSI activé mais colonne 'rsi' absente")
                    return False

                if use_ma and 'trend_score' not in first_result:
                    print("❌ ERREUR: MA activées mais colonne 'trend_score' absente")
                    return False

                if not use_rsi and 'rsi' in first_result:
                    print("⚠️  AVERTISSEMENT: RSI désactivé mais colonne 'rsi' présente")
        else:
            print("✅ Test réussi: Aucune paire ne correspond aux critères (normal)")

        return True

    except Exception as e:
        print(f"❌ Test échoué: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Restaurer la configuration
        config.USE_RSI = original_rsi
        config.USE_MA = original_ma
        config.MAX_PAIRS = original_max


def main():
    """
    Exécute tous les tests de configuration
    """
    print("\n" + "=" * 80)
    print("🧪 TESTS DES CONFIGURATIONS D'INDICATEURS")
    print("=" * 80)

    tests = [
        {
            'name': 'Configuration 1 - RSI uniquement',
            'use_rsi': True,
            'use_ma': False,
            'description': 'Scanner V1 classique avec RSI seul'
        },
        {
            'name': 'Configuration 2 - Moyennes Mobiles uniquement',
            'use_rsi': False,
            'use_ma': True,
            'description': 'Scanner de tendance sans RSI'
        },
        {
            'name': 'Configuration 3 - RSI + MA (V1.5)',
            'use_rsi': True,
            'use_ma': True,
            'description': 'Filtre combiné optimal'
        },
        {
            'name': 'Configuration 4 - Aucun indicateur',
            'use_rsi': False,
            'use_ma': False,
            'description': 'Scan sans filtrage (liste brute)'
        }
    ]

    results_summary = []

    for test in tests:
        success = test_configuration(
            test['name'],
            test['use_rsi'],
            test['use_ma'],
            test['description']
        )
        results_summary.append({
            'name': test['name'],
            'success': success
        })

    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)

    total = len(results_summary)
    passed = sum(1 for r in results_summary if r['success'])
    failed = total - passed

    for result in results_summary:
        status = "✅ RÉUSSI" if result['success'] else "❌ ÉCHOUÉ"
        print(f"{status} - {result['name']}")

    print("-" * 80)
    print(f"Total: {passed}/{total} tests réussis")

    if failed > 0:
        print(f"⚠️  {failed} test(s) échoué(s)")
        sys.exit(1)
    else:
        print("✅ Tous les tests sont passés avec succès!")
        sys.exit(0)


if __name__ == "__main__":
    main()
