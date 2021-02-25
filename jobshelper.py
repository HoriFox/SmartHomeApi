from crontab import CronTab

class SchedulerManager():
    def __init__(self, api, plan_list, logger):
        self.logger = logger
        self.api = api
        cron = CronTab(user=True)
        job = cron.new(command='echo hello_world')
        job.minute.every(1)
        cron.write()
        # При первом запуске подгружаем все задания в очередь
        self.load_plan(plan_list)

    def load_plan(self, plan_list):
        if len(plan_list) != 0:
            for elem in plan_list:
                self.create_plan(str(elem['PlanId']), elem['PlanDays'],
                                    elem['PlanTime'], 'relay', elem['ModuleIp'])

    def create_plan(self, plan_id, plan_days, plan_time, module_type, module_ip):
        print('[!]Load plan:\n')
        print('[P]Id:', plan_id, '\n' +
                '[P]Days:',  plan_days, '\n' +
                '[P]Time:', plan_time, '\n' +
                '[P]Type module:', module_type, '\n' +
                '[P]Module ip', module_ip, '\n')

        week_list = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        # Переводим указанные дни недели в числа 0-6
        day_of_week = ','.join([str(week_list.index(plan_day))
                                for plan_day in plan_days.split(' ')])
        time_all = plan_time.split(' ')
        hour_start, minute_start = time_all[0].split(':')

        cron_string = '%s %s * * %s' % (minute_start, hour_start, day_of_week)
        print('Cron style:', cron_string)

        #if(len(time_all) == 2):
        #        hour_end,·minute_end·=·time_all[1].split(':')
        #        cron_string = '%s %s * * %s' % (minute_end, hour_end, day_of_week)
        #        print('Cron style:', cron_string)


        #Стартовое время
        #id_job = plan_id + 'start'
        #self.scheduler.add_job(self.job_worker, 'cron',
        #                        day_of_week=day_of_week,
        #                        hour=hour_start,
        #                        minute=minute_start,
        #                        id = id_job,
        #                        replace_existing = True,
        #                        kwargs=dict(module_type=module_type,
        #                                    module_ip=module_ip,
        #                                    stage='start'))

        #Если есть конечное время
        #if len(time_all) == 2:
        #    hour_end, minute_end = time_all[1].split(':')
        #    id_job = plan_id + 'end'
        #    self.scheduler.add_job(self.job_worker, 'cron',
        #                            day_of_week=day_of_week,
        #                            hour=hour_end,
        #                            minute=minute_end,
        #                            id = id_job,
        #                            replace_existing = True,
        #                            kwargs=dict(module_type=module_type,
        #                                        module_ip=module_ip,
        #                                        stage='end'))

    def delete_plan(self, id_jobs):
        id_job_start = id_jobs + 'start'
        if id_job_start in self.scheduler.get_jobs():
            self.scheduler.remove_job(id_job_start)
        id_job_end = id_jobs + 'end'
        if id_job_end in self.scheduler.get_jobs():
            self.scheduler.remove_job(id_job_end)

    def on_exit(self):
        self.scheduler.shutdown()
        self.logger.info('SERVER: Scheduler shutdown')

    def job_worker(self, module_type, stage, module_ip):
        if module_type == 'relay':
            value = '1' if stage == 'start' else '0'
            self.api.run_api({'type':'relay', 'value':value, 'ip':module_ip})
