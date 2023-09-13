# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "hashicorp/bionic64"
  config.vm.provision :docker

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 4096
    vb.customize ['modifyvm', :id, '--usb', 'on']
    # M5StickV https://devicehunt.com/view/type/usb/vendor/0403/device/6001
    vb.customize ['usbfilter', 'add', '0', '--target', :id, '--name', 'FT232', '--vendorid', '0403', '--productid', '6001']
    # Amigo + Bit https://devicehunt.com/view/type/usb/vendor/0403/device/6010
    vb.customize ['usbfilter', 'add', '0', '--target', :id, '--name', 'FT2232', '--vendorid', '0403', '--productid', '6010']
    # Dock https://devicehunt.com/view/type/usb/vendor/1a86/device/7523
    vb.customize ['usbfilter', 'add', '0', '--target', :id, '--name', 'CH340', '--vendorid', '1a86', '--productid', '7523']
  end
end

class VagrantPlugins::ProviderVirtualBox::Config < Vagrant.plugin("2", :config)
  def update_customizations(customizations)
    @customizations = customizations
  end
end

class VagrantPlugins::ProviderVirtualBox::Action::Customize
  alias_method :original_call, :call
  def call(env)
    machine = env[:machine]
    config = machine.provider_config
    driver = machine.provider.driver
    uuid = driver.instance_eval { @uuid }
    if uuid != nil
      lines = driver.execute('showvminfo', uuid, '--machinereadable', retryable: true).split("\n")
      filters = {}
      lines.each do |line|
        if matcher = /^USBFilterVendorId(\d+)="(.+?)"$/.match(line)
          id = matcher[1].to_i
          vendor_id = matcher[2].to_s
          filters[id] ||= {}
          filters[id][:vendor_id] = vendor_id
        elsif matcher = /^USBFilterProductId(\d+)="(.+?)"$/.match(line)
          id = matcher[1].to_i
          product_id = matcher[2].to_s
          filters[id] ||= {}
          filters[id][:product_id] = product_id
        end
      end
      config.update_customizations(config.customizations.reject { |_, command| filter_exists(filters, command) })
    end
    original_call(env)
  end

  def filter_exists(filters, command)
    if command.size > 6 && command[0] == 'usbfilter' && command[1] == 'add'
      vendor_id = product_id = false
      i = 2
      while i < command.size - 1 do
        if command[i] == '--vendorid'
          i += 1
          vendor_id = command[i]
        elsif command[i] == '--productid'
          i += 1
          product_id = command[i]
        end
        i += 1
      end
      if vendor_id != false && product_id != false
        filters.each do |_, filter|
          if filter[:vendor_id] == vendor_id && filter[:product_id] == product_id
            return true
          end
        end
      end
    end
    return false
  end
end
