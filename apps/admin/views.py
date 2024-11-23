# @Time    : 2023/8/14 14:38
# @Author  : Lan
# @File    : views.py
# @Software: PyCharm
import datetime

from fastapi import APIRouter, Depends
from apps.admin.services import FileService, ConfigService, LocalFileService
from apps.admin.dependencies import admin_required, get_file_service, get_config_service, get_local_file_service
from apps.admin.schemas import IDData, ShareItem, DeleteItem
from core.response import APIResponse
from apps.base.models import FileCodes, KeyValue

admin_api = APIRouter(prefix='/admin', tags=['管理'])


@admin_api.post('/login')
async def login(admin: bool = Depends(admin_required)):
    return APIResponse()


@admin_api.get('/dashboard')
async def dashboard(admin: bool = Depends(admin_required)):
    all_codes = await FileCodes.all()
    all_size = str(sum([code.size for code in all_codes]))
    sys_start = await KeyValue.filter(key='sys_start').first()
    # 获取当前日期时间
    now = datetime.datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - datetime.timedelta(days=1)
    yesterday_end = today_start - datetime.timedelta(microseconds=1)
    # 统计昨天一整天的记录数（从昨天0点到23:59:59）
    yesterday_codes = FileCodes.filter(
        created_at__gte=yesterday_start,
        created_at__lte=yesterday_end
    )
    # 统计今天到现在的记录数（从今天0点到现在）
    today_codes = FileCodes.filter(
        created_at__gte=today_start
    )
    return APIResponse(detail={
        'totalFiles': len(all_codes),
        'storageUsed': all_size,
        'sysUptime': sys_start.value,
        'yesterdayCount': await yesterday_codes.count(),
        'yesterdaySize': str(sum([code.size for code in await yesterday_codes])),
        'todayCount': await today_codes.count(),
        'todaySize': str(sum([code.size for code in await today_codes])),
    })


@admin_api.delete('/file/delete')
async def file_delete(
        data: IDData,
        file_service: FileService = Depends(get_file_service),
        admin: bool = Depends(admin_required)
):
    await file_service.delete_file(data.id)
    return APIResponse()


@admin_api.get('/file/list')
async def file_list(
        page: int = 1,
        size: int = 10,
        file_service: FileService = Depends(get_file_service),
        admin: bool = Depends(admin_required)
):
    files, total = await file_service.list_files(page, size)
    return APIResponse(detail={
        'page': page,
        'size': size,
        'data': files,
        'total': total,
    })


@admin_api.get('/config/get')
async def get_config(
        config_service: ConfigService = Depends(get_config_service),
        admin: bool = Depends(admin_required)
):
    return APIResponse(detail=config_service.get_config())


@admin_api.patch('/config/update')
async def update_config(
        data: dict,
        config_service: ConfigService = Depends(get_config_service),
        admin: bool = Depends(admin_required)
):
    await config_service.update_config(data)
    return APIResponse()


@admin_api.get('/file/download')
async def file_download(
        id: int,
        file_service: FileService = Depends(get_file_service),
        admin: bool = Depends(admin_required)
):
    file_content = await file_service.download_file(id)
    return file_content


@admin_api.get('/local/lists')
async def get_local_lists(
        local_file_service: LocalFileService = Depends(get_local_file_service),
        admin: bool = Depends(admin_required)
):
    files = await local_file_service.list_files()
    return APIResponse(detail=files)


@admin_api.delete('/local/delete')
async def delete_local_file(
        item: DeleteItem,
        local_file_service: LocalFileService = Depends(get_local_file_service),
        admin: bool = Depends(admin_required)
):
    result = await local_file_service.delete_file(item.filename)
    return APIResponse(detail=result)


@admin_api.post('/local/share')
async def share_local_file(
        item: ShareItem,
        file_service: FileService = Depends(get_file_service),
        admin: bool = Depends(admin_required)
):
    share_info = await file_service.share_local_file(item)
    return APIResponse(detail=share_info)
