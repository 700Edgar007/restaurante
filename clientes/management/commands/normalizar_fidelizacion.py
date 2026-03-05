from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from clientes.models import OportunidadRuleta, PremioCliente


class Command(BaseCommand):
    help = (
        'Limpia datos historicos de fidelizacion creados por reglas antiguas '
        '(giros bonus_spin_* y bonos 8% antiguos).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--aplicar',
            action='store_true',
            help='Aplica cambios en base de datos. Sin este flag solo muestra el diagnostico.',
        )

    def handle(self, *args, **options):
        aplicar = options['aplicar']

        qs_giros_legacy = OportunidadRuleta.objects.filter(accion__startswith='bonus_spin_')
        qs_giros_legacy_pendientes = qs_giros_legacy.filter(usada=False)

        qs_descuentos_legacy = PremioCliente.objects.filter(
            Q(descripcion__startswith='Bono fidelidad: 8%')
            | Q(descripcion__icontains='8% en tu siguiente pedido'),
            tipo='DESCUENTO',
            activo=True,
            usado=False,
        )

        total_giros_legacy = qs_giros_legacy.count()
        total_giros_legacy_pendientes = qs_giros_legacy_pendientes.count()
        total_descuentos_legacy = qs_descuentos_legacy.count()

        self.stdout.write(self.style.WARNING('Diagnostico de normalizacion:'))
        self.stdout.write(f'- Giros legacy (bonus_spin_*): {total_giros_legacy}')
        self.stdout.write(f'- Giros legacy pendientes: {total_giros_legacy_pendientes}')
        self.stdout.write(f'- Descuentos legacy 8% pendientes: {total_descuentos_legacy}')

        if not aplicar:
            self.stdout.write(self.style.WARNING('Modo simulacion: no se aplicaron cambios.'))
            self.stdout.write('Ejecuta con --aplicar para confirmar la limpieza.')
            return

        ahora = timezone.now()

        actualizados_giros = qs_giros_legacy_pendientes.update(
            usada=True,
            premio='Ajuste de normalizacion',
            puntos_otorgados=0,
            usada_en=ahora,
        )

        actualizados_descuentos = qs_descuentos_legacy.update(
            activo=False,
            usado=True,
            descripcion='Ajuste de normalizacion: bono legacy desactivado',
        )

        self.stdout.write(self.style.SUCCESS('Normalizacion aplicada correctamente.'))
        self.stdout.write(f'- Giros normalizados: {actualizados_giros}')
        self.stdout.write(f'- Bonos legacy desactivados: {actualizados_descuentos}')
