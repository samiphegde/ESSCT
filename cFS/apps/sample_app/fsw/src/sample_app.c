#include "sample_app_events.h"
#include "sample_app_version.h"
#include "sample_app.h"
#include "sample_app_msgids.h"
#include "sample_app_msg.h"
#include "sample_app_perfids.h"

#include "cfe.h"
#include <string.h> // for memset
#include <unistd.h> // for usleep

SAMPLE_APP_Data_t SAMPLE_APP_Data;

void SAMPLE_APP_Main(void)
{
    int32 status;
    CFE_SB_Buffer_t *SBBufPtr;

    /* Register the app with Executive Services */
    CFE_ES_RegisterApp();

    /* Register event filter table */
    CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);

    /* Create command pipe */
    CFE_SB_CreatePipe(&SAMPLE_APP_Data.CommandPipe, 10, "SAMPLE_APP_CMD_PIPE");

    /* Subscribe to command and send telemetry requests */
    CFE_SB_Subscribe(SAMPLE_APP_CMD_MID, SAMPLE_APP_Data.CommandPipe);
    CFE_SB_Subscribe(SAMPLE_APP_SEND_HK_MID, SAMPLE_APP_Data.CommandPipe);

    /* Initialize telemetry message */
    CFE_MSG_Init((CFE_MSG_Message_t *)&SAMPLE_APP_Data.HkTlm,
                 CFE_SB_ValueToMsgId(SAMPLE_APP_HK_TLM_MID),
                 sizeof(SAMPLE_APP_Data.HkTlm));

    SAMPLE_APP_Data.Counter = 0;

    CFE_EVS_SendEvent(SAMPLE_APP_STARTUP_INF_EID, CFE_EVS_EventType_INFORMATION,
                      "Sample App Started - Sending periodic telemetry");

    SAMPLE_APP_Data.RunStatus = CFE_ES_RunStatus_APP_RUN;

    while (CFE_ES_RunLoop(&SAMPLE_APP_Data.RunStatus) == true)
    {
        // Send telemetry every second
        SAMPLE_APP_Data.Counter++;

        SAMPLE_APP_Data.HkTlm.Payload.CommandErrorCounter = 0;
        SAMPLE_APP_Data.HkTlm.Payload.CommandCounter = SAMPLE_APP_Data.Counter;

        CFE_SB_TimeStampMsg((CFE_MSG_Message_t *)&SAMPLE_APP_Data.HkTlm);
        CFE_SB_SendMsg((CFE_MSG_Message_t *)&SAMPLE_APP_Data.HkTlm);

        CFE_EVS_SendEvent(SAMPLE_APP_COMMAND_INF_EID, CFE_EVS_EventType_DEBUG,
                          "Sent telemetry packet #%u", (unsigned int)SAMPLE_APP_Data.Counter);

        // Sleep for 1 second (1,000,000 microseconds)
        usleep(1000000);
    }

    CFE_ES_ExitApp(SAMPLE_APP_Data.RunStatus);
}
