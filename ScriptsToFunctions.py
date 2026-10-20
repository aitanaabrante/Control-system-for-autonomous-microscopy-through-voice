from InitialConnection import client
import asyncio 

def Example_MessageChat1():
    client.PyApiMessageChat.Model.Message = "Hello, this is LasxApi from VS Code"
    confirmed = client.PyApiMessageChat.UpdateSync(5)
    print(f"MessageChat:[{'OK' if confirmed else 'Timeout'}]")

def Example_GetConfocalHardwareInfo1():
    client.PyApiCommand.Model.Command = "GetConfocalHardwareInfo"   
    confirmed = client.PyApiCommand.UpdateSync(15)
    if(client.PyApiCommandEcho.Model.HasError):
        print("Error:\n" + client.PyApiCommandEcho.Model.Error)
    print(f"GetConfocalHardwareInfo:[{"OK" if confirmed else "Timeout"}]: HWInfo: {client.PyApiGetConfocalHardwareInfo.Model.HWInfo}")

def Example_AssignJob1():
    job_name = "Overview"
    assign_job_type = client.PyApiAssignJob.Model.AssignJobType
    client.PyApiAssignJob.Model.AssignJobType = type(assign_job_type).EAssignToAllScanFields
    client.PyApiAssignJob.Model.JobName = job_name
    confirmed = client.PyApiAssignJob.UpdateSync(15)
    if(client.PyApiCommandEcho.Model.HasError):
        print("Error:\n" + client.PyApiCommandEcho.Model.Error)
    print(f"PyApiAssignJob :[{"OK" if confirmed else "Timeout"}]: assigning: {job_name}")

async def Example_AcquireJob1():
    client.PyApiAcquireJob.Model.JobName = 'HiRes'
    confirmed = client.PyApiAcquireJob.UpdateSync(30)
    if(client.PyApiCommandEcho.Model.HasError):
        print("Error:\n" + client.PyApiCommandEcho.Model.Error)
    print(f"PyApiAcquireJob:[{"OK" if confirmed else "Timeout"}]")
    print(f"Waiting for scan to finish...")
    while str(client.PyApiStatusScan.Model.ScanStatus) != "ScanIsIdle":
        await asyncio.sleep(1)
    print(f"Scan done.")

def Example_LoadExperiment1():
    confirmed = False
    client.PyApiLoadExperiment.Model.ExperimentName = "ExampleExperiment1"
    confirmed = client.PyApiLoadExperiment.UpdateSync(30)
    if client.PyApiCommandEcho.Model.HasError:
        print("Error:\n" + client.PyApiCommandEcho.Model.Error)
    print(f"LoadExperiment:[{'OK' if confirmed else 'Timeout'}] {client.PyApiLoadExperiment.Model.ExperimentName}")
    confirmed = False
    client.PyApiCommand.Model.Command = "GetExperimentInformation"
    confirmed = client.PyApiCommand.UpdateSync(30)
    if client.PyApiCommandEcho.Model.HasError:
        print("Error:\n" + client.PyApiCommandEcho.Model.Error)
    print(f"GetExperimentInformation:[{'OK' if confirmed else 'Timeout'}]: ScanningTemplate: {client.PyApiExperimentInformation.Model.ScanningTemplate}")

def Example_StartAFScan1():
    async def waitScanIdle():
        while str(client.PyApiStatusScan.Model.ScanStatus) == "ScanIsIdle":
            print(f"waiting for start..{client.PyApiStatusScan.Model.ScanStatus}")
            await asyncio.sleep(1)
        while str(client.PyApiStatusScan.Model.ScanStatus) != "ScanIsIdle":
            print(f"waiting for end..{client.PyApiStatusScan.Model.ScanStatus}")
            await asyncio.sleep(1)
        print("AF Scan Done.")
    confirmed = client.PyApiStartAFScan.UpdateSync(30)
    print(f"PyApiStartAFScan:[{'OK' if confirmed else 'Timeout'}] scanStatus: {client.PyApiStatusScan.Model.ScanStatus}")
    print("Waiting async...")
    try:
        asyncio.run(waitScanIdle())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(waitScanIdle())