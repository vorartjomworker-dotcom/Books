# Снимок реестров ошибок CH05–CH09

Дата переноса: 2026-08-16.

Канонические файлы Google Drive прочитаны без изменения. В закрытый GitHub-репозиторий добавлены неизменённые экспортные копии и извлечённая вкладка CH09.

## Состав

| Глава | Результат |
|---|---|
| CH05 | Отдельный актуальный реестр не найден; добавлена поясняющая запись со ссылкой на канонический реестр v0.3. Старый файл из другой папки не переносился. |
| CH06 | Перенесён отдельный реестр глубокого аудита v0.1. |
| CH07 | Перенесён отдельный реестр v0.7 с отметкой `BATCH-003_CORRECTIONS_VERIFIED`. |
| CH08 | Нативный Google Sheet экспортирован в XLSX как v0.1. |
| CH09 | Вкладка `Ошибки` извлечена из канонического нативного реестра v0.2 в CSV: 30 записей, все со статусом `CLOSED`. |
| CH05–CH09 | Перенесён сводный реестр вопросов и рисков v0.3. |

## Файлы и контрольные суммы

| Путь | Drive ID | Байт | SHA-256 |
|---|---|---:|---|
| `qa/issues/CH06/CH06_BATCH-001_errors_deep_audit_v0.1.xlsx` | `17l0SvKmg73BZsiXCMrf9bUqKVFg2RZvo` | 18139 | `460114bb39349f5bd61f6f25423558408f85671978aea569c3a18b01c0db2f12` |
| `qa/issues/CH07/CH07_errors_v0.7_BATCH-003_CORRECTIONS_VERIFIED.xlsx` | `1Fn9dhERzSuWhwkitdS8CHdueAoTKn-aK` | 15649 | `00ee479ca929895189b4bd6b203289717e36489868688518f02d219c95e3e789` |
| `qa/issues/CH08/CH08_errors_deep_audit_v0.1.xlsx` | `1xkx0u36hVX4bI7pUt8Qvf9ICsO_DiiyTAQEmPndnZxI` | 23674 | `e3819010abf79a049c29a4a8fc5cf48247400d95bb9448de332c64b3df42c2bb` |
| `qa/issues/CH05_CH09_risks_v0.3.xlsx` | `1r5c3EzYiQ91IGlN4cvQzdx89LmeLLpfS` | 5953 | `136582aaa3ebd456b6b4d2d6776d35bb7772c3e921720f253fda326ec08c72c4` |
| `qa/issues/CH09/CH09_errors_from_registry_v0.2.csv` | `1gEuN0ZoRT4hK_sMAgLAnB1upB7zprVTvCB8X2YlV2Bw` | 29946 | `66fa067c508874099bde75783bfebaa0806a07f822e3fbc8e60168309f35bc58` |
| `qa/issues/CH05/README.md` | — | 716 | `49642fb7f0e3aa67fbc61818d08b14a05df7e0961bc3440f7c1cad10f40fcf7d` |

## Примечания

- Файлы в `qa/issues/` являются датированным Git-снимком; исходники в Google Drive остаются каноническими.
- CSV CH09 содержит отображаемые значения диапазона `Ошибки!A1:Z200`; фактически заполнено 31 строка с заголовком.
- Реестр CH08 экспортирован из Google Sheets в XLSX, поэтому размер экспортной копии может отличаться от размера нативного объекта Drive.
