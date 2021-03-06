import datetime
import pytz

from django.db.models import Count
from django.urls import reverse
from django.views.generic import TemplateView

from .settings import TIME_ZONE
from .admin import TinhAdmin
from .models import HoDan, CuuHo, TinhNguyenVien


class IndexView(TemplateView):
    template_name = "home_index.html"
    compare_time = datetime.datetime(
        2020, 10, 26, 17, 0, 0, tzinfo=datetime.timezone.utc
    ).astimezone(tz=pytz.timezone(TIME_ZONE))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tong_hodan_da_duoc_cuu"] = HoDan.objects.filter(status_id=7).count()
        context["tong_hodan_cap_cuu"] = HoDan.objects.filter(status_id=3).count()
        context["tong_doi_cuu_ho_san_sang"] = CuuHo.objects.filter(status=1).count()
        context["tong_tinh_nguyen_vien"] = TinhNguyenVien.objects.count()
        context["tinh_infos"] = []

        hodan_url = reverse("admin:app_hodan_changelist")
        hodan_da_cuu = self._get_ho_dan_da_cuu_by_tinh()
        cuuho_by_tinh = self._get_cuu_ho_by_tinh()
        hodan_can_cuu = self._get_ho_dan_can_cuu_by_tinh()

        # Các danh sách hộ dân cần cứu và đã cứu, và danh sách cứu hộ đều được sort theo id của tỉnh,
        # nên thứ tự là giống nhau.
        for ind, val in enumerate(hodan_can_cuu):
            info = {
                "url": f'{hodan_url}?{TinhAdmin.URL_CUSTOM_TAG}={val["tinh_id"]}',
            }
            info.update(val)
            info.update(hodan_da_cuu[ind])
            info.update(cuuho_by_tinh[ind])
            context["tinh_infos"].append(info)

        return context

    def _get_ho_dan_can_cuu_by_tinh(self):
        """
        Lấy tất cả Hộ Dân cần cứu rồi group lại theo tỉnh.
        Return:
            list of dict: Sort theo id của tỉnh
            [
                {
                    "tinh__name": Quảng Bình,
                    "tinh_id": 1,
                    "can_cuu_count": 10
                },
                {
                    "tinh__name": Quảng Bình,
                    "tinh_id": 2,
                    "can_cuu_count": 10
                },
                ...
            ]
        """
        ho_dan_can_cuu_by_tinh = (
            HoDan.objects.filter(created_time__gt=self.compare_time)
            .exclude(status_id=7)
            .values("tinh__name", "tinh_id")
            .annotate(can_cuu_count=Count("tinh"))
        )
        sorted_can_cuu_by_tinh = sorted(
            ho_dan_can_cuu_by_tinh, key=lambda i: i["tinh_id"]
        )

        return sorted_can_cuu_by_tinh

    def _get_ho_dan_da_cuu_by_tinh(self):
        """
        Lấy tất cả Hộ Dân đã cứu rồi group lại theo tỉnh.
        Return:
            list of dict: Sort theo id của tỉnh
            [
                {
                    "tinh__name": Quảng Bình,
                    "tinh_id": 1,
                    "da_cuu_count": đã10
                },
                {
                    "tinh__name": Quảng Bình,
                    "tinh_id": 2,
                    "da_cuu_count": 10
                },
                ...
            ]
        """
        ho_dan_da_cuu_by_tinh = (
            HoDan.objects.filter(created_time__gt=self.compare_time, status_id=7)
            .values("tinh__name", "tinh_id")
            .annotate(da_cuu_count=Count("tinh"))
        )

        sorted_da_cuu_by_tinh = sorted(
            ho_dan_da_cuu_by_tinh, key=lambda i: i["tinh_id"]
        )

        return sorted_da_cuu_by_tinh

    def _get_cuu_ho_by_tinh(self):
        """
        Lấy danh sách tất cả Cứu Hộ rồi group lại theo tỉnh.
        Return:
            list of dict: Sort theo id của tỉnh
            [
                {
                    "tinh__name": Quảng Bình,
                    "tinh_id": 1,
                    "cuu_ho_count": 10
                },
                {
                    "tinh__name": Quảng Bình,
                    "tinh_id": 2,
                    "cuu_ho_count": 10
                },
                ...
            ]
        """
        cuu_ho_tinh = CuuHo.objects.values("tinh__name", "tinh_id").annotate(
            cuu_ho_count=Count("tinh")
        )
        sorted_cuu_ho_by_tinh = sorted(cuu_ho_tinh, key=lambda i: i["tinh_id"])
        return sorted_cuu_ho_by_tinh
